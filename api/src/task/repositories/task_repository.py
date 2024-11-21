from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from src.db.models import Task
from src.share.base_repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """
    Repository class for handling CRUD operations on the Task model.
    """

    def get_by_id(self, db_session: Session, id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Retrieves a task by its ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the task.
            user_id (UUID): The ID of the user making the request.

        Returns:
            Optional[Task]: The task if found, otherwise None.
        """
        return db_session.query(Task).filter(Task.id == id, Task.user_id == user_id).first()

    def get_all(self, db_session: Session, user_id: UUID) -> list[Task]:
        """
        Retrieves all tasks for a given user.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The ID of the user whose tasks to fetch.

        Returns:
            List[Task]: A list of tasks belonging to the user.
        """
        return db_session.query(Task).filter(Task.user_id == user_id).all()

    def create(self, db_session: Session, task: Task) -> Task:
        """
        Creates a new task.

        Args:
            db_session (Session): The database session to use.
            task (Task): The task instance to add.

        Returns:
            Task: The created task instance.
        """
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    def update(self, db_session: Session, id: UUID, task_data: dict, user_id: UUID) -> Task:
        """
        Updates an existing task.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the task to update.
            task_data (dict): A dictionary of fields to update.
            user_id (UUID): The ID of the user making the request.

        Returns:
            Task: The updated task instance.
        """
        task = self.get_by_id(db_session, id, user_id)
        if not task:
            raise Exception("Task not found")
        for key, value in task_data.items():
            setattr(task, key, value)
        db_session.commit()
        db_session.refresh(task)
        return task

    def delete(self, db_session: Session, id: UUID, user_id: UUID) -> None:
        """
        Deletes a task by its ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the task to delete.
            user_id (UUID): The ID of the user making the request.

        Raises:
            Exception: If the task is not found.
        """
        task = self.get_by_id(db_session, id, user_id)
        if not task:
            raise Exception("Task not found")
        db_session.delete(task)
        db_session.commit()
