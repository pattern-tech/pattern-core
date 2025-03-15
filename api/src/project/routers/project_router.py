from uuid import UUID
from typing import List, Dict
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.execptions import NotFoundError
from src.auth.utils.get_token import authenticate_user
from src.project.services.project_service import ProjectService
from src.util.response import global_response, GlobalResponse, ExceptionResponse

router = APIRouter(prefix="/project")
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


def get_project_service() -> ProjectService:
    """
    Dependency to instantiate the ProjectService.
    """
    return ProjectService()


class CreateProjectInput(BaseModel):
    """
    Schema for creating a project.
    """
    name: str
    workspace_id: UUID

    class Config:
        from_attributes = True


class ProjectOutput(BaseModel):
    """
    Schema for project output.
    """
    id: UUID
    name: str
    workspace_id: UUID

    class Config:
        from_attributes = True


@router.post(
    "",
    response_model=GlobalResponse[ProjectOutput, Dict],
    summary="Create Project",
    description="Creates a new project for the authenticated user within a specified workspace.",
    response_description="The created project data.",
    responses={
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    }
)
def create_project(
    input: CreateProjectInput,
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
    user_id: UUID = Depends(authenticate_user)
):
    """
    Create a new project.

    - **input**: The project creation input containing the project name and workspace ID.
    - **db**: Database session.
    - **service**: Project service handling business logic.
    - **user_id**: The authenticated user's ID.

    Returns:
        ProjectOutput: The created project data.
    """
    try:
        project = service.create_project(
            db, input.name, user_id, input.workspace_id)
        return global_response(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{project_id}",
    response_model=GlobalResponse[ProjectOutput, Dict],
    summary="Get Project",
    description="Retrieves a project by its ID for the authenticated user.",
    response_description="The project data.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Project not found"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    }
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Retrieve a project by its ID.

    - **project_id**: The ID of the project to retrieve.
    - **db**: Database session.
    - **service**: Project service handling business logic.
    - **user_id**: The authenticated user's ID.

    Returns:
        ProjectOutput: The project data.
    """
    try:
        project = service.get_project(db, project_id, user_id)
        return global_response(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "",
    response_model=GlobalResponse[List[ProjectOutput], Dict],
    summary="List All Projects",
    description="Lists all projects for the authenticated user.",
    response_description="A list of all projects for the user.",
    responses={
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    }
)
def get_all_projects(
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    List all projects for the authenticated user.

    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Project service handling business logic.

    Returns:
        List[ProjectOutput]: A list of all projects for the user.
    """
    projects = service.get_all_projects(db, user_id)
    return global_response(projects)


@router.put(
    "/{project_id}",
    response_model=GlobalResponse[ProjectOutput, Dict],
    summary="Update Project",
    description="Updates an existing project by its ID for the authenticated user.",
    response_description="The updated project data.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Project not found"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request received"
        }
    }
)
def update_project(
    project_id: UUID,
    input: CreateProjectInput,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Update an existing project.

    - **project_id**: The ID of the project to update.
    - **input**: The project update input containing the new name and workspace ID.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Project service handling business logic.

    Returns:
        ProjectOutput: The updated project data.
    """
    try:
        updated_project = service.update_project(
            db, project_id, input.dict(), user_id)
        return global_response(updated_project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Project",
    description="Deletes a project by its ID for the authenticated user.",
    response_description="The project is successfully deleted.",
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "Project not found"
        },
        400: {
                "model": ExceptionResponse,
                "description": "Bad request received"
            }
    }
)
def delete_project(
    project_id: UUID,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Delete a project by its ID.

    - **project_id**: The ID of the project to delete.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Project service handling business logic.

    Returns:
        None: If the project is successfully deleted.
    """
    try:
        project = service.delete_project(db, project_id, user_id)
        return global_response(project)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
