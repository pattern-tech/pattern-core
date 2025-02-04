import os
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.util.encryption import encrypt_message
from src.auth.utils.get_token import authenticate_user
from src.tool.services.tool_service import ToolService

router = APIRouter(prefix="/tool")
database = Database()


def get_db():
    """
    Dependency to get a SQLAlchemy database session.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_tool_service() -> ToolService:
    """
    Dependency to instantiate the ToolService.
    """
    return ToolService()


class ToolOutput(BaseModel):
    """
    Schema for tool output.
    """
    id: UUID
    name: str
    function_name: str
    description: str
    api_key: str

    class Config:
        orm_mode = True


@router.get(
    "/{project_id}",
    summary="Search Tools",
    description=(
        "Searches for tools based on the provided project ID and an optional query string and active status. "
        "Results are paginated using limit and offset parameters."
    ),
    response_description="A paginated list of tools that match the search criteria."
)
def get_all_tools(
    project_id: UUID,
    query: Optional[str] = "",
    active: Optional[bool] = None,
    limit: int = 10,
    offset: int = 0,
    db_session: Session = Depends(get_db),
    service: ToolService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Search for tools based on a query.

    - **project_id**: The ID of the project to search tools in.
    - **query**: The search keyword (default is an empty string).
    - **active**: Optional filter for active status (True/False). If not provided, no filter is applied.
    - **limit**: Number of items to retrieve per page (default: 10).
    - **offset**: Number of items to skip (default: 0).
    - **db_session**: Database session dependency.
    - **service**: Tool service handling business logic.
    - **_**: The authenticated user's ID (not used in the function logic).

    Returns:
        dict: A dictionary containing:
            - **content**: List of tools (as defined by ToolOutput) that match the search criteria.
            - **metadata**: Pagination metadata including total_count, limit, and offset.
    """
    tools, total_count = service.get_all_tools(
        db_session, project_id, query, active, limit, offset
    )

    metadata = {
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
    }

    return global_response(content=tools, metadata=metadata)
