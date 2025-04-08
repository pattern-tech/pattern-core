from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from langchain_core.messages.human import HumanMessage

from src.util.configuration import Config
from src.util.execptions import NotFoundError
from src.db.models import Conversation, QueryUsage
from src.agentflow.utils.shared_tools import init_llm
from src.user.services.user_service import UserService
from src.agent.services.memory_service import MemoryService
from src.project.services.project_service import ProjectService
from src.agent.services.agent_service import RouterAgentService
from src.project.repositories.project_repository import ProjectRepository
from src.query_usage.services.query_usage_service import QueryUsageService
from src.conversation.repositories.conversation_repository import ConversationRepository

from src.agentflow.tools.indexing import FunctionIndexer, FunctionSchema
from src.agentflow.utils.tools_index import get_all_tools
from src.agentflow.core.code_generattion import CodeGenerator


class ConversationService:
    """
    Service class for handling conversation-related business logic.
    """

    def __init__(self):
        self.repository = ConversationRepository()
        self.project_repository = ProjectRepository()
        # self.memory_service = MemoryService()
        self.project_service = ProjectService()
        # self.query_usage_service = QueryUsageService()
        self.user_service = UserService()

    def create_conversation(
        self, db_session: Session, name: str, project_id: UUID, user_id: UUID, conversation_id: UUID = None
    ) -> Conversation:
        """
        Creates a new conversation.

        Args:
            db_session (Session): The database session.
            name (str): The name of the conversation.
            project_id (UUID): The ID of the project the conversation belongs to.
            user_id (UUID): The ID of the user creating the conversation.
            conversation_id (UUID): The ID of the conversation (optional).

        Returns:
            Conversation: The created conversation instance.
        """
        if name.strip() == "":
            raise Exception("Name is required")

        if not self.project_repository.get_by_id(db_session, project_id, user_id):
            raise NotFoundError("Project not exists or not owned by user")

        conversation = Conversation(
            name=name, project_id=project_id, user_id=user_id)

        # conversation id is generated in frontend
        if conversation_id:
            conversation.id = conversation_id

        return self.repository.create(db_session, conversation)

    def get_conversation(
        self, db_session: Session, conversation_id: UUID, user_id: UUID
    ) -> Conversation:
        """
        Retrieves a conversation by its ID.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to retrieve.
            project_id (UUID): The ID of the project the conversation belongs to.

        Returns:
            Conversation: The conversation instance.

        Raises:
            Exception: If the conversation is not found.
        """
        conversation = self.repository.get_by_id(
            db_session, conversation_id, user_id)

        messages = self.get_history(
            db_session, user_id, conversation_id)

        if not conversation:
            raise NotFoundError("Conversation not found")

        return conversation, messages

    def get_all_conversations(self, db_session: Session, project_id: UUID, user_id: UUID) -> List[Conversation]:
        """
        Lists all conversations for a specific project.

        Args:
            db_session (Session): The database session.
            project_id (UUID): The ID of the project to retrieve conversations for.
            user_id (UUID): The ID of the user who owns the project.

        Returns:
            List[Conversation]: A list of Conversation instances.
        """
        if not self.project_service.get_project(db_session, project_id, user_id):
            raise NotFoundError("Project not exists or not owned by user")

        return self.repository.get_all(db_session, project_id)

    def update_conversation(
        self, db_session: Session, conversation_id: UUID, data: dict, user_id: UUID
    ) -> Conversation:
        """
        Updates a conversation with the given data.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to update.
            data (dict): A dictionary containing the fields to update.
            user_id (UUID): The ID of the user updating the conversation.

        Returns:
            Conversation: The updated conversation instance.

        Raises:
            Exception: If the conversation is not found.
        """
        if data["name"].strip() == "":
            raise Exception("Name is required")

        if not self.project_repository.get_by_id(db_session, data["project_id"], user_id):
            raise NotFoundError("Project not exists or not owned by user")

        return self.repository.update(db_session, conversation_id, data, user_id)

    def delete_conversation(
        self, db_session: Session, conversation_id: UUID, user_id: UUID
    ) -> None:
        """
        Deletes a conversation.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to delete.
            user_id (UUID): The ID of the user deleting the conversation.

        Returns:
            None
        """
        self.repository.delete(db_session, conversation_id, user_id)

    def get_project_associated_with_conversation(self, db_session: Session, conversation_id: UUID) -> UUID:
        """
        Retrieves the project ID associated with a conversation.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation.

        Returns:
            UUID: The project ID associated with the conversation.
        """
        return self.repository.get_project_associated_with_conversation(db_session, conversation_id)

    def send_message(
        self,
        db_session: Session,
        message: str,
        user_id: UUID,
        conversation_id: UUID,
        project_id: UUID,
        message_type: str,
        stream: bool
    ):
        """
        Asynchronously processes and sends a message, either streaming the response token-by-token or returning a complete response.

        Args:
            db_session (Session): Database session for database operations
            message (str): The message to be processed
            user_id (UUID): ID of the user sending the message
            conversation_id (UUID): ID of the conversation the message belongs to
            project_id (UUID): ID of the project associated with the conversation
            message_type (str): Type of the message
            stream (bool): If True, streams response tokens. If False, returns complete response

        Returns:
            If stream=True:
                Generator yielding individual response tokens
            If stream=False:
                Dict containing:
                    - response (str): Complete response text
                    - intermediate_steps (List[Dict]): List of executed tool steps

        Raises:
            Exception: If associated project is not found
        """
        conversation = self.repository.get_by_id(
            db_session, conversation_id, user_id)

        if not conversation:
            raise NotFoundError(
                "Conversation not found or is not owned by user")

        if conversation.project_id != project_id:
            raise NotFoundError("Project not found or is not owned by user")

        indexer = FunctionIndexer()

        functions = indexer.search_functions(query=message, limit=5)

        print('chose functions\n-------------------')
        for fn in functions:
            print(fn.payload["function_name"], fn.score)
        print('-------------------\n\n')

        if not functions:
            print('not functions')
            functions = []
            chain_scan_tools = get_all_tools("chain_scan_tools")
            moralis_tools = get_all_tools("moralis_tools")

            functions.extend(chain_scan_tools)
            functions.extend(moralis_tools)

            for function in functions:
                inp_schema = function["input_schema"] if "input_schema" in function.keys(
                ) else None
                out_schema = function["output_schema"] if "output_schema" in function.keys(
                ) else None
                fn_schema = FunctionSchema(function_name=function["name"],
                                           description=function["description"],
                                           input_schema=inp_schema,
                                           output_schema=out_schema)

                indexer.index_function(fn_schema)
                print(f'indexed {function["name"]}')

        functions = indexer.search_functions(query=message, limit=5)

        imports = "from src.agentflow.providers.chain_scan_tools import *\nfrom src.agentflow.providers.moralis_tools import *"

        code_generator = CodeGenerator()
        code_generator.set_user_input(message)
        code_generator.set_tools_schema(functions)
        result, error, code = code_generator.generate_and_execute(imports)

        return result

    def get_history(
        self,
        db_session: Session,
        user_id: UUID,
        conversation_id: UUID,
    ):
        """
        Get conversation history for a given conversation.

        Args:f
            db_session (Session): Database session
            user_id (UUID): ID of the user requesting history
            conversation_id (UUID): ID of the conversation to get history for

        Returns:
            list: List of message dictionaries containing:
                - role (str): Either "human" or "ai" indicating message sender
                - content (str): Message content
                - additional_kwargs (dict): Additional message metadata
                - response_metadata (dict): Response metadata for AI messages
        """
        memory = self.memory_service.get_memory(conversation_id)

        history = []
        generated_id = 0
        for message in memory.messages:
            history.append({
                "id": generated_id,
                "role": "human" if isinstance(message, HumanMessage) else "ai",
                "content": message.content,
            })
            generated_id += 1
        return history

    def rename_title(self, db_session: Session, conversation_id: UUID, user_id: UUID, message: str) -> str:
        """
        Renames a conversation title using the LLM to generate a title.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to rename.
            user_id (UUID): The ID of the user renaming the conversation.
            message (str): The message to generate a title for.

        Returns:
            str: The new title of the conversation.
        """
        config = Config.get_config()
        self.llm = init_llm(service=config["llm"]["provider"],
                            model_name=config["llm"]["model"],
                            api_key=config["llm"]["api_key"],
                            stream=False,
                            callbacks=None)
        messages = [
            (
                "system",
                "You should generate a title (maximum 5 words) for this message",
            ),
            ("human", f"{message}"),
        ]

        title = self.llm.invoke(messages)

        self.repository.update(db_session, conversation_id, {
                               "name": title.content}, user_id)

        return title.content
