from uuid import UUID
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.auth.utils.get_token import authenticate_user
from src.workspace.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspace")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_workspace_service() -> WorkspaceService:
    return WorkspaceService()


class CreateWorkspaceInput(BaseModel):
    name: str

    class Config:
        orm_mode = True


class WorkspaceOutput(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


@router.post("", response_model=WorkspaceOutput)
def create_workspace(
    input: CreateWorkspaceInput,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Creates a new workspace.

    Args:
        input (CreateWorkspaceInput): The workspace creation input

    Returns:
        WorkspaceOutput: The created workspace data

    Raises:
        HTTPException: If workspace creation fails
    """
    try:
        workspace = service.create_workspace(db, input.name, user_id)
        return global_response(workspace)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{workspace_id}", response_model=WorkspaceOutput)
def get_workspace(
    workspace_id: UUID,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Retrieves a workspace by its ID.

    Args:
        workspace_id (UUID): The workspace ID

    Returns:
        WorkspaceOutput: The workspace data

    Raises:
        HTTPException: If the workspace is not found
    """
    try:
        workspace = service.get_workspace(db, workspace_id, user_id)
        return global_response(workspace)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[WorkspaceOutput])
def get_all_workspaces(
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Lists all workspaces for the authenticated user.

    Returns:
        List[WorkspaceOutput]: List of all user workspaces
    """
    workspaces = service.get_all_workspaces(db, user_id)
    return global_response(workspaces)


@router.put("/{workspace_id}", response_model=WorkspaceOutput)
def update_workspace(
    workspace_id: UUID,
    input: CreateWorkspaceInput,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Updates an existing workspace by its ID.

    Args:
        workspace_id (UUID): The workspace ID

    Returns:
        WorkspaceOutput: The updated workspace data

    Raises:
        HTTPException: If the update fails
    """
    try:
        workspace = service.update_workspace(
            db, workspace_id, input.model_dump(), user_id
        )
        return global_response(workspace)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: UUID,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Deletes a workspace by its ID.

    Args:
        workspace_id (UUID): The workspace ID

    Returns:
        None: If the workspace is successfully deleted

    Raises:
        HTTPException: If deletion fails
    """
    try:
        workspace = service.delete_workspace(db, workspace_id, user_id)
        return global_response(workspace)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
