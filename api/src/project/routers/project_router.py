from uuid import UUID
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.auth.utils.get_token import authenticate_user
from src.project.services.project_service import ProjectService
from typing import Set

router = APIRouter(prefix="/project")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_project_service() -> ProjectService:
    return ProjectService()


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


class ToolOutput(BaseModel):
    id: UUID
    function_name: str
    description: str

    class Config:
        orm_mode = True


class ModifyToolInput(BaseModel):
    project_id: UUID
    tools_id: Set[UUID]


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

    Returns:
        ProjectOutput: The project data.
    """
    try:
        project = service.get_project(db, project_id, user_id)
        return global_response(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[ProjectOutput])
def get_all_projects(
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Lists all projects for the current user.

    Returns:
        List[ProjectOutput]: List of all projects for the user.
    """
    projects = service.get_all_projects(db, user_id)
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

    Returns:
        ProjectOutput: The updated project data.
    """
    try:
        updated_project = service.update_project(
            db, project_id, input.dict(), user_id)
        return global_response(updated_project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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

    Returns:
        None
    """
    try:
        project = service.delete_project(db, project_id, user_id)
        return global_response(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{project_id}/tools", response_model=List[ToolOutput])
def get_project_tools(
    project_id: UUID,
    limit: int = 10,  # Default number of items per page
    offset: int = 0,  # Default starting point
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Retrieves all tools associated with a project with pagination.

    Args:
        project_id (UUID): The project ID.
        limit (int): Maximum number of items to return per page. Defaults to 10.
        offset (int): Number of items to skip. Defaults to 0.
        user_id (UUID): ID of the authenticated user.
        db (Session): Database session.
        service (ProjectService): Project service instance.

    Returns:
        dict: Dictionary containing:
            - items (List[Tool]): List of tools associated with the project
            - total_count (int): Total number of tools returned
            - limit (int): Maximum items per page
            - offset (int): Number of items skipped
    """
    try:
        tools, total_count = service.get_project_tools(
            db, project_id, limit, offset)
        return global_response({
            "items": tools,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/tools", response_model=List[ToolOutput])
def modify_project_tools(
    input: ModifyToolInput,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Adds a tool to a project.

    Args:
        project_id (UUID): The project ID.
        tools_id (Set[UUID]): The tool ID.

    Returns:
        None
    """
    try:
        tools = service.modify_project_tools(
            db, input.project_id, input.tools_id)
        return global_response(tools)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
