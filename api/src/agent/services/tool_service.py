from uuid import uuid4
from sqlalchemy.orm import Session

from src.db.models import Tool
from src.agent.repositories.tool_repositoy import ToolRepository
from src.vectordb.services.vectordb_service import VectorDBService
from langchain_core.documents import Document


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
            api_key=api_key,  # TODO: Hash api key
        )
        self.repository.create(db_session, tool)

        self.vector_service.add_documents(documents, [vector_id])

    def tools_picker(self, query: str, k: int = 3):
        # TODO: Optimize by score
        filter = {"source": "pattern"}
        results = self.vector_service.similarity_search(query=query, k=k, filter=filter)
        function_names = []
        for result in results:
            function_names.append(result[0].metadata["function_name"])

        return function_names

    def get_tool_by_function_name(self, db_session: Session, function_name: str):
        return self.repository.get_by_function_name(db_session, function_name)
