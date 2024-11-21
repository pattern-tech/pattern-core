from uuid import UUID
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.auth.utils.get_token import authenticate_user
from src.project.services.project_service import ProjectService
from src.project.repositories.project_repository import ProjectRepository

router = APIRouter(prefix="/project")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_project_service() -> ProjectService:
    repository = ProjectRepository()
    return ProjectService(repository)


class CreateProjectInput(BaseModel):
    name: str
    workspace_id: UUID

    class Config:
        orm_mode = True


class ProjectOutput(BaseModel):
    id: UUID
    name: str
    workspace_id: UUID

    class Config:
        orm_mode = True


@router.post("", response_model=ProjectOutput)
def create_project(
    input: CreateProjectInput,
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Creates a new project.

    Args:
        input (CreateProjectInput): The project creation input.
        db (Session): SQLAlchemy session.
        service (ProjectService): Project service instance.
        user_id (UUID): ID of the current user.

    Returns:
        ProjectOutput: The created project data.
    """
    try:
        project = service.create_project(
            db, input.name, user_id, input.workspace_id)
        return global_response(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/{project_id}", response_model=ProjectOutput)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Retrieves a project by its ID.

    Args:
        project_id (UUID): The project ID.
        db (Session): SQLAlchemy session.
        service (ProjectService): Project service instance.
        user_id (UUID): ID of the current user.

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


@router.get("", response_model=List[ProjectOutput])
def list_projects(
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Lists all projects for the current user.

    Args:
        db (Session): SQLAlchemy session.
        service (ProjectService): Project service instance.
        user_id (UUID): ID of the current user.

    Returns:
        List[ProjectOutput]: List of all projects for the user.
    """
    projects = service.list_projects(db, user_id)
    return global_response(projects)


@router.put("/{project_id}", response_model=ProjectOutput)
def update_project(
    project_id: UUID,
    input: CreateProjectInput,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Updates an existing project by its ID.

    Args:
        project_id (UUID): The project ID.
        input (CreateProjectInput): Updated project data.
        db (Session): SQLAlchemy session.
        service (ProjectService): Project service instance.
        user_id (UUID): ID of the current user.

    Returns:
        ProjectOutput: The updated project data.
    """
    try:
        updated_project = service.update_project(db, project_id, input.dict(), user_id)
        return global_response(updated_project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Deletes a project by its ID.

    Args:
        project_id (UUID): The project ID.
        db (Session): SQLAlchemy session.
        service (ProjectService): Project service instance.
        user_id (UUID): ID of the current user.

    Returns:
        None
    """
    try:
        project = service.delete_project(db, project_id, user_id)
        return global_response(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
