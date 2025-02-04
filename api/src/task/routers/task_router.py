from uuid import UUID
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.auth.utils.get_token import authenticate_user
from src.task.services.task_service import TaskService
from fastapi import HTTPException

router = APIRouter(prefix="/task")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_service() -> TaskService:
    return TaskService()


class CreateTaskInput(BaseModel):
    project_id: UUID
    task: str

    class Config:
        orm_mode = True


class UpdateTaskInput(BaseModel):
    task: str

    class Config:
        orm_mode = True


class TaskOutput(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    name: str
    prompt: str
    status: str
    response: str
    extra_data: dict
    project_id: UUID

    class Config:
        orm_mode = True


@router.post("", response_model=TaskOutput)
def create_task(
    input: CreateTaskInput,
    db: Session = Depends(get_db),
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Creates a new task.

    Args:
        input (CreateTaskInput): The input data for creating a task.

    Returns:
        TaskOutput: The created task data.
    """

    try:
        task = service.create_task(
            db,
            input.project_id,
            user_id,
            input.task,
        )
        return global_response(task)
    except Exception as e:
        raise e


@router.get("/{task_id}", response_model=TaskOutput)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Retrieves a task by its ID.

    Args:
        task_id (UUID): The task ID.

    Returns:
        TaskOutput: The task data.
    """
    try:
        task = service.get_task(db, task_id, user_id)
        return global_response(task)
    except Exception as e:
        raise e


@router.get("", response_model=List[TaskOutput])
def get_all_tasks(
    db: Session = Depends(get_db),
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Lists all tasks for the current user.

    Returns:
        List[TaskOutput]: List of task data.
    """
    tasks = service.get_all_tasks(db, user_id)
    return global_response(tasks)


@router.put("/{task_id}", response_model=TaskOutput)
def update_task(
    task_id: UUID,
    input: UpdateTaskInput,
    db: Session = Depends(get_db),
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Updates an existing task.

    Args:
        task_id (UUID): The task ID.

    Returns:
        TaskOutput: The updated task data.
    """
    try:

        # TODO : fix this
        return HTTPException(status_code=501, detail="Not implemented yet")

        updated_task = service.update_task(db, task_id, input.task, user_id)
        return global_response(updated_task)
    except Exception as e:
        raise e


@router.delete("/{task_id}")
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(authenticate_user),
):
    """
    Deletes a task by its ID.

    Args:
        task_id (UUID): The task ID.

    Returns:
        None
    """
    try:
        # TODO : fix this
        return HTTPException(status_code=501, detail="Not implemented yet")

        deleted_task = service.delete_task(db, task_id, user_id)
        return global_response(deleted_task)
    except Exception as e:
        raise e
