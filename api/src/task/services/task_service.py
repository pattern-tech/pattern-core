from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from src.task.enum.task_status_enum import TaskStatusEnum
from src.db.models import Task
from src.task.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(
        self, db_session: Session, project_id: UUID, user_id: UUID, prompt: str
    ) -> Task:
        """
        Creates a new task.

        Args:
            db_session (Session): The database session.
            project_id (UUID): The ID of the project to which the task belongs.
            user_id (UUID): The ID of the user creating the task.
            prompt (str): The prompt for the task.
            status (str): The status of the task.
            name (str): Optional name of the task.
            response (str): Optional response to the task.
            extra_data (dict): Optional extra data related to the task.

        Returns:
            Task: The created task instance.
        """
        task = Task(
            project_id=project_id,
            user_id=user_id,
            prompt=prompt,
            status=TaskStatusEnum.INIT,
        )
        return self.repository.create(db_session, task)

    def get_task(self, db_session: Session, task_id: UUID, user_id: UUID) -> Task:
        """
        Retrieves a task by its ID.

        Args:
            db_session (Session): The database session.
            task_id (UUID): The ID of the task to retrieve.
            user_id (UUID): The ID of the user.

        Returns:
            Task: The task instance.

        Raises:
            Exception: If the task is not found.
        """
        task = self.repository.get_by_id(db_session, task_id, user_id)
        if not task:
            raise Exception("Task not found")
        return task

    def list_tasks(self, db_session: Session, user_id: UUID) -> List[Task]:
        """
        Lists all tasks for a user.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user.

        Returns:
            List[Task]: A list of Task instances.
        """
        return self.repository.get_all(db_session, user_id)

    def update_task(
        self, db_session: Session, task_id: UUID, task_data: dict, user_id: UUID
    ) -> Task:
        """
        Updates an existing task.

        Args:
            db_session (Session): The database session.
            task_id (UUID): The ID of the task to update.
            task_data (dict): A dictionary of fields to update.
            user_id (UUID): The ID of the user.

        Returns:
            Task: The updated Task instance.
        """
        return self.repository.update(db_session, task_id, task_data, user_id)

    def delete_task(self, db_session: Session, task_id: UUID, user_id: UUID) -> None:
        """
        Deletes a task by its ID.

        Args:
            db_session (Session): The database session.
            task_id (UUID): The ID of the task to delete.
            user_id (UUID): The ID of the user.

        Returns:
            None
        """
        self.repository.delete(db_session, task_id, user_id)
