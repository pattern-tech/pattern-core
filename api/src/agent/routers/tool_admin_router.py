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
