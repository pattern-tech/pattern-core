from uuid import UUID
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.exceptions import NotFoundError
from src.auth.utils.get_token import authenticate_user
from src.workspace.services.workspace_service import WorkspaceService
from src.util.response import global_response, GlobalResponse, ExceptionResponse

router = APIRouter(prefix="/workspace")
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


def get_workspace_service() -> WorkspaceService:
    """
    Dependency to instantiate the WorkspaceService.
    """
    return WorkspaceService()


class CreateWorkspaceInput(BaseModel):
    """
    Schema for creating a workspace.
    """
    name: str = Field(..., example="New Workspace")

    class Config:
        from_attributes = True


class WorkspaceOutput(BaseModel):
    """
    Schema for workspace output.
    """
    id: UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    name: str = Field(..., example="New Workspace")
    created_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")
    updated_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")
    deleted_at: datetime = Field(None, example="2025-03-15T15:30:20+03:30")

    class Config:
        from_attributes = True


@router.post(
    "",
    response_model=GlobalResponse[WorkspaceOutput, Dict],
    summary="Create Workspace",
    description="Creates a new workspace for the authenticated user.",
    response_description="The created workspace data.",
    responses={
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received."
        },
    },
)
def create_workspace(
    input: CreateWorkspaceInput,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Create a new workspace.

    - **input**: The workspace creation input containing the workspace name.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Workspace service handling business logic.

    Returns:
        WorkspaceOutput: The newly created workspace details.
    """
    try:
        workspace = service.create_workspace(db, input.name, user_id)
        return global_response(workspace)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/{workspace_id}",
    response_model=GlobalResponse[WorkspaceOutput, Dict],
    summary="Get Workspace",
    description="Retrieves a workspace by its ID for the authenticated user.",
    response_description="The workspace data.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Workspace not found."
        },
    },
)
def get_workspace(
    workspace_id: UUID,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Retrieve a workspace by its ID.

    - **workspace_id**: The ID of the workspace to retrieve.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Workspace service handling business logic.

    Returns:
        WorkspaceOutput: The workspace details if found.
    """
    try:
        workspace = service.get_workspace(db, workspace_id, user_id)
        return global_response(workspace)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "",
    response_model=GlobalResponse[List[WorkspaceOutput], Dict],
    summary="List All Workspaces",
    description="Lists all workspaces for the authenticated user.",
    response_description="A list of all workspaces data."
)
def get_all_workspaces(
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    List all workspaces for the authenticated user.

    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Workspace service handling business logic.

    Returns:
        List[WorkspaceOutput]: A list of all the user's workspaces.
    """
    workspaces = service.get_all_workspaces(db, user_id)
    return global_response(workspaces)


@router.put(
    "/{workspace_id}",
    response_model=GlobalResponse[WorkspaceOutput, Dict],
    summary="Update Workspace",
    description="Updates an existing workspace by its ID for the authenticated user.",
    response_description="The updated workspace data.",
    responses={
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received."
        },
    },
)
def update_workspace(
    workspace_id: UUID,
    input: CreateWorkspaceInput,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Update an existing workspace.

    - **workspace_id**: The ID of the workspace to update.
    - **input**: The workspace update input containing the new workspace name.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Workspace service handling business logic.

    Returns:
        WorkspaceOutput: The updated workspace details.
    """
    try:
        workspace = service.update_workspace(
            db, workspace_id, input.model_dump(), user_id
        )
        return global_response(workspace)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Workspace",
    description="Deletes a workspace by its ID for the authenticated user.",
    response_description="The workspace is successfully deleted.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Workspace not found"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    },
)
def delete_workspace(
    workspace_id: UUID,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Delete a workspace by its ID.

    - **workspace_id**: The ID of the workspace to delete.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Workspace service handling business logic.

    Returns:
        None: If the workspace is successfully deleted.
    """
    try:
        workspace = service.delete_workspace(db, workspace_id, user_id)
        return global_response(workspace)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
