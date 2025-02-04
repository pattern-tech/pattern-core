from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import join

from src.db.models import SubTask, Task
from src.share.base_repository import BaseRepository


class SubTaskRepository(BaseRepository[SubTask]):
    """
    Repository class for handling CRUD operations on the SubTask model.
    """

    def get_by_id(
        self, db_session: Session, id: UUID, user_id: UUID
    ) -> Optional[SubTask]:
        """
        Retrieves a sub-task by its ID, ensuring it belongs to a task owned by the user.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the sub-task.
            user_id (UUID): The ID of the user making the request.

        Returns:
            Optional[SubTask]: The sub-task if found, otherwise None.
        """
        return (
            db_session.query(SubTask)
            .join(Task)
            .filter(SubTask.id == id, Task.user_id == user_id)
            .first()
        )

    def get_all(self, db_session: Session, user_id: UUID) -> List[SubTask]:
        """
        Retrieves all sub-tasks for a given user.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The ID of the user whose sub-tasks to fetch.

        Returns:
            List[SubTask]: A list of sub-tasks belonging to the user.
        """
        return (
            db_session.query(SubTask).join(Task).filter(Task.user_id == user_id).all()
        )

    def create(self, db_session: Session, sub_task: SubTask) -> SubTask:
        """
        Creates a new sub-task.

        Args:
            db_session (Session): The database session to use.
            sub_task (SubTask): The sub-task instance to add.

        Returns:
            SubTask: The created sub-task instance.
        """
        db_session.add(sub_task)
        db_session.commit()
        db_session.refresh(sub_task)
        return sub_task

    def update(
        self, db_session: Session, id: UUID, sub_task_data: dict, user_id: UUID
    ) -> SubTask:
        """
        Updates an existing sub-task.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the sub-task to update.
            sub_task_data (dict): A dictionary of fields to update.
            user_id (UUID): The ID of the user making the request.

        Returns:
            SubTask: The updated sub-task instance.
        """
        sub_task = self.get_by_id(db_session, id, user_id)
        if not sub_task:
            raise Exception("Sub-task not found")
        for key, value in sub_task_data.items():
            setattr(sub_task, key, value)
        db_session.commit()
        db_session.refresh(sub_task)
        return sub_task

    def delete(self, db_session: Session, id: UUID, user_id: UUID) -> None:
        """
        Deletes a sub-task by its ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the sub-task to delete.
            user_id (UUID): The ID of the user making the request.

        Raises:
            Exception: If the sub-task is not found.
        """
        sub_task = self.get_by_id(db_session, id, user_id)
        if not sub_task:
            raise Exception("Sub-task not found")
        db_session.delete(sub_task)
        db_session.commit()
