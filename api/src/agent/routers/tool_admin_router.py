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
from src.agent.services.tool_service import ToolAdminService

router = APIRouter(prefix="/admin/tool")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_tool_service() -> ToolAdminService:
    return ToolAdminService()


class ToolOutput(BaseModel):
    id: UUID
    name: str
    function_name: str
    description: str
    api_key: str

    class Config:
        orm_mode = True


class CreateToolInput(BaseModel):
    name: str = ...
    description: str = ...
    function_name: str = ...
    api_key: Optional[str] = None

    class Config:
        orm_mode = True


@router.post("")
def create_tool(
    input: CreateToolInput,
    db: Session = Depends(get_db),
    service: ToolAdminService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Creates a new tool.

    Args:
        input (CreateToolInput): The tool creation input.

    Returns:
        ProjectOutput: The created tool data.
    """
    try:

        secrete_key = os.getenv("SECRET_KEY")

        if secrete_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="secrete key not found")

        if input.api_key is not None:

            api_key = encrypt_message(
                message=input.api_key,
                password=secrete_key)
        else:
            api_key = None

        project = service.create_tool(
            db, input.name, input.description, input.function_name, api_key
        )
        return global_response(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/")
def search_tools(
    query: Optional[str] = "",
    active: Optional[bool] = None,
    limit: int = 10,  # Default number of items per page
    offset: int = 0,  # Default starting point
    db_session: Session = Depends(get_db),
    service: ToolAdminService = Depends(get_tool_service),
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
    try:
        tools, total_count = service.search_tools(
            db_session, query, active, limit, offset)
        return global_response({
            "items": tools,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/id/{tool_id}")
def get_tool_by_id(
    tool_id: UUID,
    db_session: Session = Depends(get_db),
    service: ToolAdminService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Retrieves a single tool by its ID.

    Args:
        tool_id (UUID): The ID of the tool to retrieve.
        db_session (Session): Database session.
        service (ToolAdminService): Tool service instance.

    Returns:
        Tool: The tool with the specified ID.
    """
    try:
        tool = service.get_tool_by_id(db_session, tool_id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found"
            )
        return global_response(tool)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/fn_name/{function_name}")
def get_tool_by_function_name(
    function_name: str,
    db_session: Session = Depends(get_db),
    service: ToolAdminService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Retrieves a single tool by its function name.

    Args:
        function_name (str): The function name of the tool to retrieve.
        db_session (Session): Database session.
        service (ToolAdminService): Tool service instance.

    Returns:
        Tool: The tool with the specified function name.
    """
    try:
        tool = service.get_tool_by_function_name(db_session, function_name)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found"
            )
        return global_response(tool)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
