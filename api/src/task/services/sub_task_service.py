from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session

from src.db.models import SubTask
from src.task.repositories.sub_task_repository import SubTaskRepository
from src.task.repositories.task_repository import TaskRepository


class SubTaskService:
    def __init__(self):
        self.repository = SubTaskRepository()
        self.task_repository = TaskRepository()

    def create_sub_task(
        self,
        db_session: Session,
        task_id: UUID,
        project_id: UUID,
        user_id: UUID,
        sub_task: str,
        status: str,
        name: Optional[str] = None,
        priority: Optional[int] = None,
        order: Optional[int] = None,
        response: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ) -> SubTask:
        """
        Creates a new sub-task.

        Args:
            db_session (Session): The database session.
            task_id (UUID): The ID of the task to which the sub-task belongs.
            project_id (UUID): The ID of the project to which the sub-task belongs.
            name (Optional[str]): The name of the sub-task.
            task (str): The prompt for the sub-task.
            status (str): The status of the sub-task.
            priority (Optional[int]): The priority of the sub-task.
            order (Optional[int]): The order of the sub-task.
            response (Optional[str]): The response of the sub-task.
            extra_data (Optional[dict]): Any extra data for the sub-task.
            user_id (UUID): The ID of the user.

        Returns:
            SubTask: The created sub-task instance.
        """

        # Verify that the task exists and belongs to the user
        task = self.task_repository.get_by_id(db_session, task_id, user_id)
        if not task:
            raise Exception("Task not found or does not belong to the user")

        if task.project_id != project_id:
            raise Exception("Project ID does not match the task's project ID")

        new_sub_task = SubTask(
            task_id=task_id,
            project_id=project_id,
            name=name,
            sub_task=sub_task,
            status=status,
            priority=priority,
            order=order,
            response=response,
            extra_data=extra_data,
        )
        sub_task = self.repository.create(db_session, new_sub_task)
        return sub_task

    def get_sub_task(
        self, db_session: Session, sub_task_id: UUID, user_id: UUID
    ) -> SubTask:
        """
        Retrieves a sub-task by its ID.

        Args:
            db_session (Session): The database session.
            sub_task_id (UUID): The ID of the sub-task to retrieve.
            user_id (UUID): The ID of the user.

        Returns:
            SubTask: The sub-task instance.

        Raises:
            Exception: If the sub-task is not found.
        """
        sub_task = self.repository.get_by_id(db_session, sub_task_id, user_id)
        if not sub_task:
            raise Exception("Sub-task not found")
        return sub_task

    def list_sub_tasks(self, db_session: Session, user_id: UUID) -> List[SubTask]:
        """
        Lists all sub-tasks for a user.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user.

        Returns:
            List[SubTask]: A list of SubTask instances.
        """
        return self.repository.get_all(db_session, user_id)

    def update_sub_task(
        self, db_session: Session, sub_task_id: UUID, sub_task_data: dict, user_id: UUID
    ) -> SubTask:
        """
        Updates an existing sub-task.

        Args:
            db_session (Session): The database session.
            sub_task_id (UUID): The ID of the sub-task to update.
            sub_task_data (dict): A dictionary of fields to update.
            user_id (UUID): The ID of the user.

        Returns:
            SubTask: The updated SubTask instance.
        """
        return self.repository.update(db_session, sub_task_id, sub_task_data, user_id)

    def delete_sub_task(
        self, db_session: Session, sub_task_id: UUID, user_id: UUID
    ) -> None:
        """
        Deletes a sub-task by its ID.

        Args:
            db_session (Session): The database session.
            sub_task_id (UUID): The ID of the sub-task to delete.
            user_id (UUID): The ID of the user.

        Returns:
            None
        """
        self.repository.delete(db_session, sub_task_id, user_id)
