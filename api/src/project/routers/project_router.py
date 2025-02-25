from uuid import UUID
from typing import List, Set
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.auth.utils.get_token import authenticate_user
from src.project.services.project_service import ProjectService

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
        orm_mode = True


class ProjectOutput(BaseModel):
    """
    Schema for project output.
    """
    id: UUID
    name: str
    workspace_id: UUID

    class Config:
        orm_mode = True


class ToolOutput(BaseModel):
    """
    Schema for tool output.
    """
    id: UUID
    function_name: str
    description: str

    class Config:
        orm_mode = True


class ModifyToolInput(BaseModel):
    """
    Schema for modifying project tools.
    """
    project_id: UUID
    tools_id: Set[UUID]


@router.post(
    "",
    response_model=ProjectOutput,
    summary="Create Project",
    description="Creates a new project for the authenticated user within a specified workspace.",
    response_description="The created project data."
)
def create_project(
    input: CreateProjectInput,
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
    user_id: UUID = Depends(authenticate_user),
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
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/{project_id}",
    response_model=ProjectOutput,
    summary="Get Project",
    description="Retrieves a project by its ID for the authenticated user.",
    response_description="The project data."
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
    response_model=List[ProjectOutput],
    summary="List All Projects",
    description="Lists all projects for the authenticated user.",
    response_description="A list of all projects for the user."
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
    response_model=ProjectOutput,
    summary="Update Project",
    description="Updates an existing project by its ID for the authenticated user.",
    response_description="The updated project data."
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
    response_description="The project is successfully deleted."
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/{project_id}/tools",
    response_model=List[ToolOutput],
    summary="Get Project Tools",
    description="Retrieves all tools associated with a project with pagination.",
    response_description="A list of tools associated with the project along with pagination metadata."
)
def get_project_tools(
    project_id: UUID,
    limit: int = 10,  # Default number of items per page
    offset: int = 0,  # Default starting point
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Retrieve tools associated with a project with pagination.

    - **project_id**: The ID of the project.
    - **limit**: Maximum number of items to return per page (default is 10).
    - **offset**: Number of items to skip (default is 0).
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Project service handling business logic.

    Returns:
        dict: A dictionary containing:
            - items (List[ToolOutput]): List of tools associated with the project.
            - total_count (int): Total number of tools.
            - limit (int): Maximum items per page.
            - offset (int): Number of items skipped.
    """
    try:
        tools, total_count = service.get_project_tools(
            db, project_id, limit, offset)
        metadata = {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        }
        return global_response(content=tools, metadata=metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/tools",
    response_model=List[ToolOutput],
    summary="Modify Project Tools",
    description="Adds or modifies tools associated with a project for the authenticated user.",
    response_description="A list of updated tools associated with the project."
)
def modify_project_tools(
    input: ModifyToolInput,
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: ProjectService = Depends(get_project_service),
):
    """
    Modify tools for a project.

    - **input**: The input containing the project ID and a set of tool IDs.
    - **user_id**: The authenticated user's ID.
    - **db**: Database session.
    - **service**: Project service handling business logic.

    Returns:
        List[ToolOutput]: The updated list of tools associated with the project.
    """
    try:
        tools = service.modify_project_tools(
            db, input.project_id, input.tools_id)
        return global_response(tools)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
