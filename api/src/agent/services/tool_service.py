from uuid import uuid4
from sqlalchemy.orm import Session

from src.db.models import Tool
from src.agent.repositories.tool_repositoy import ToolRepository
from src.vectordb.services.vectordb_service import VectorDBService
from langchain_core.documents import Document
from uuid import UUID


class ToolAdminService:
    def __init__(self):
        self.vector_service = VectorDBService()
        self.repository = ToolRepository()

    def create_tool(
        self,
        db_session: Session,
        name: str,
        description: str,
        function_name: str,
        api_key: str = None,
    ):
        db_id = uuid4()
        vector_id = str(uuid4())

        documents = [
            Document(
                page_content=f"""
                Name: {name}\nDescription: {description}
                """,
                metadata={
                    "db_id": db_id,
                    "source": "pattern",
                    "tool_name": name,
                    "function_name": function_name,
                },
            )
        ]

        tool = Tool(
            id=db_id,
            name=name,
            description=description,
            vector_id=vector_id,
            function_name=function_name,
            api_key=api_key,
        )
        self.repository.create(db_session, tool)

        self.vector_service.add_documents(documents, [vector_id])

    def tools_picker(self, query: str, k: int = 3):
        # TODO: Optimize by score
        filter = {"source": "pattern"}
        results = self.vector_service.similarity_search(
            query=query, k=k, filter=filter)
        function_names = []
        for result in results:
            function_names.append(result[0].metadata["function_name"])

        return function_names

    def get_all_tools(self, db_session: Session, limit: int, offset: int):
        """
        Fetches tools with pagination.

        Args:
            db_session (Session): The database session.
            limit (int): Number of items to fetch.
            offset (int): Number of items to skip.

        Returns:
            List[Tool]: A list of tools.
        """
        return self.repository.get_all(db_session, limit, offset)

    def get_tool_by_id(self, db_session: Session, id: UUID):
        """
        Retrieves a single tool by its ID.

        Args:
            db_session (Session): The database session.
            id (UUID): The ID of the tool to retrieve.

        Returns:
            Tool: The tool with the specified ID.
        """
        return self.repository.get_by_id(db_session, id)

    def get_tool_by_function_name(self, db_session: Session, function_name: str):
        """
        Retrieves a single tool by its function name.

        Args:
            db_session (Session): The database session.
            function_name (str): The function name of the tool to retrieve.

        Returns:
            Tool: The tool with the specified function name.
        """
        return self.repository.get_by_function_name(db_session, function_name)

    def search_tools(
        self, db_session: Session, query: str, active: bool, limit: int, offset: int
    ):
        """
        Searches for tools based on the query and optional filters.

        Args:
            db_session (Session): The database session.
            query (str): The search keyword.
            active (Optional[bool]): Filter by active status (True/False). Default is no filter.
            limit (int): Number of items to retrieve.
            offset (int): Number of items to skip.

        Returns:
            tuple: A tuple containing the list of tools and total count.
        """
        tools, total_count = self.repository.search_tools(
            db_session, query, active, limit, offset)
        return tools, total_count

    def get_tool_count(self, db_session: Session):
        """
        Retrieves the total count of tools.

        Args:
            db_session (Session): The database session.

        Returns:
            int: The total count of tools.
        """
        return self.repository.get_tool_count(db_session)
