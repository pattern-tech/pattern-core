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
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_tool_service() -> ToolService:
    return ToolService()


class ToolOutput(BaseModel):
    id: UUID
    name: str
    function_name: str
    description: str
    api_key: str

    class Config:
        orm_mode = True


@router.get("/{project_id}")
def get_all_tools(
    project_id: UUID,
    query: Optional[str] = "",
    active: Optional[bool] = None,
    limit: int = None,
    offset: int = None,
    db_session: Session = Depends(get_db),
    service: ToolService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Searches for tools based on a query.

    Args:
        query (str): The search keyword.
        active (Optional[bool]): Filter by active status (True/False). Default is no filter.
        limit (int): Number of items to retrieve (default: 10).
        offset (int): Number of items to skip (default: 0).

    Returns:
        dict: A list of tools matching the search query, with pagination.
    """
    tools, total_count = service.get_all_tools(
        db_session, project_id, query, active, limit, offset)

    metadata = {
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
    }

    return global_response(content=tools, metadata=metadata)
