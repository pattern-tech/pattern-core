import io
import os
import csv

from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.util.encryption import encrypt_message
from src.auth.utils.get_token import authenticate_user
from src.agent.services.tool_service import ToolAdminService

router = APIRouter(prefix="/admin/tool")
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


def get_tool_service() -> ToolAdminService:
    """
    Dependency to instantiate the ToolAdminService.
    """
    return ToolAdminService()


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


class CreateToolInput(BaseModel):
    """
    Schema for creating a tool.
    """
    name: str = ...
    description: str = ...
    function_name: str = ...
    api_key: Optional[str] = None

    class Config:
        orm_mode = True


@router.post(
    "",
    summary="Create Tool",
    description="Creates a new tool with the provided details. If an API key is provided, it is encrypted using the SECRET_KEY.",
    response_description="The created tool data."
)
def create_tool(
    input: CreateToolInput,
    db: Session = Depends(get_db),
    service: ToolAdminService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Create a new tool.

    - **input**: The tool creation input containing name, description, function_name, and optional api_key.
    - **db**: Database session.
    - **service**: ToolAdminService handling business logic.
    - **_**: The authenticated user's ID (not used directly).

    Returns:
        The created tool data.
    """
    try:
        secret_key = os.getenv("SECRET_KEY")
        if secret_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Secret key not found"
            )

        if input.api_key is not None:
            api_key = encrypt_message(
                message=input.api_key, password=secret_key)
        else:
            api_key = None

        tool = service.create_tool(
            db, input.name, input.description, input.function_name, api_key)
        return global_response(tool)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/upload_csv",
    summary="Upload Tools via CSV",
    description=(
        "Uploads a CSV file containing tool data and creates the tools. "
        "The CSV file must have the following columns: name, description, function_name, and an optional api_key."
    ),
    response_description="A list of created tools with their names and IDs."
)
async def upload_csv_tools(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    service: ToolAdminService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Upload a CSV file to create multiple tools.

    - **file**: The CSV file containing tool data.
    - **db**: Database session.
    - **service**: ToolAdminService handling business logic.
    - **_**: The authenticated user's ID (not used directly).

    Returns:
        A dictionary containing the list of created tools (name and id).
    """
    try:
        secret_key = os.getenv("SECRET_KEY")
        if secret_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Secret key not found"
            )

        contents = await file.read()
        decoded_contents = contents.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(decoded_contents))

        created_tools: List = []
        for row in csv_reader:
            name = row.get("name")
            description = row.get("description")
            function_name = row.get("function_name")
            api_key_raw = row.get("api_key")

            # Skip creation if a tool with the same function_name already exists.
            existing_tool = service.get_tool_by_function_name(
                db, function_name)
            if existing_tool:
                continue

            api_key = None
            if api_key_raw and api_key_raw.strip():
                api_key = encrypt_message(
                    message=api_key_raw.strip(), password=secret_key)

            tool = service.create_tool(
                db, name, description, function_name, api_key)
            created_tools.append({"name": tool.name, "id": tool.id})

        return global_response(content=created_tools)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/",
    summary="Search Tools",
    description="Searches for tools based on a query and optional active status filter. Supports pagination using limit and offset.",
    response_description="A paginated list of tools that match the search criteria."
)
def search_tools(
    query: Optional[str] = "",
    active: Optional[bool] = None,
    limit: int = 10,
    offset: int = 0,
    db_session: Session = Depends(get_db),
    service: ToolAdminService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Search for tools based on a query.

    - **query**: The search keyword.
    - **active**: Optional filter for active status (True/False). If not provided, no filter is applied.
    - **limit**: Number of items to retrieve (default: 10).
    - **offset**: Number of items to skip (default: 0).
    - **db_session**: Database session.
    - **service**: ToolAdminService handling business logic.
    - **_**: The authenticated user's ID (not used directly).

    Returns:
        A dictionary containing:
            - **content**: A list of tools matching the search query.
            - **metadata**: Pagination metadata including total_count, limit, and offset.
    """
    try:
        tools, total_count = service.search_tools(
            db_session, query, active, limit, offset)
        metadata = {"total_count": total_count,
                    "limit": limit, "offset": offset}
        return global_response(content=tools, metadata=metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/id/{tool_id}",
    summary="Get Tool by ID",
    description="Retrieves a tool by its ID.",
    response_description="The tool data corresponding to the specified ID."
)
def get_tool_by_id(
    tool_id: UUID,
    db_session: Session = Depends(get_db),
    service: ToolAdminService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Retrieve a tool by its ID.

    - **tool_id**: The ID of the tool to retrieve.
    - **db_session**: Database session.
    - **service**: ToolAdminService handling business logic.
    - **_**: The authenticated user's ID (not used directly).

    Returns:
        The tool data corresponding to the specified ID.
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


@router.get(
    "/fn_name/{function_name}",
    summary="Get Tool by Function Name",
    description="Retrieves a tool by its function name.",
    response_description="The tool data corresponding to the specified function name."
)
def get_tool_by_function_name(
    function_name: str,
    db_session: Session = Depends(get_db),
    service: ToolAdminService = Depends(get_tool_service),
    _: UUID = Depends(authenticate_user),
):
    """
    Retrieve a tool by its function name.

    - **function_name**: The function name of the tool to retrieve.
    - **db_session**: Database session.
    - **service**: ToolAdminService handling business logic.
    - **_**: The authenticated user's ID (not used directly).

    Returns:
        The tool data corresponding to the specified function name.
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
