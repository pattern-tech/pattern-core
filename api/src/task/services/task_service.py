from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from src.agent.enum.agent_action_enum import AgentActionEnum
from src.task.services.sub_task_service import SubTaskService
from src.agent.services.agent_service import AgentService
from src.task.enum.task_status_enum import TaskStatusEnum
from src.db.models import Task
from src.task.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(
        self,
    ):
        self.repository = TaskRepository()
        self.agent_service = AgentService()
        self.sub_task_service = SubTaskService()

    def create_task(
        self, db_session: Session, project_id: UUID, user_id: UUID, task: str
    ) -> Task:
        """
        Creates a new task.

        Args:
            db_session (Session): The database session.
            project_id (UUID): The ID of the project to which the task belongs.
            user_id (UUID): The ID of the user creating the task.
            task (str): The prompt for the task.
            status (str): Default set to `TaskStatusEnum.INIT`

        Returns:
            Task: The created task instance.
        """
        _task = Task(
            project_id=project_id,
            user_id=user_id,
            task=task.strip(),
            status=TaskStatusEnum.INIT,
        )
        new_task = self.repository.create(db_session, _task)

        # Generate a plan for the task
        plan = self.agent_service.planner(task)

        # Check if sub-tasks can be created
        action_descriptions = ""
        allow_create_sub_tasks = True

        _count = 0
        for step in plan.steps:
            if step.action != AgentActionEnum.NO_ACTION:
                _count += 1
                action_descriptions += f"{_count}- " + step.action_description.strip()
                allow_create_sub_tasks = False

        # Create sub-tasks if allowed
        if allow_create_sub_tasks:
            for index, step in enumerate(plan.steps):
                self.sub_task_service.create_sub_task(
                    db_session,
                    new_task.id,
                    project_id,
                    user_id,
                    step.task.strip(),
                    TaskStatusEnum.INIT,
                    None,
                    None,
                    index + 1,
                )
        else:
            new_task.status = TaskStatusEnum.ACTION_REQUIRED
            db_session.commit()
            db_session.refresh(new_task)

        return {
            "task": task,
            "sub_task_created": allow_create_sub_tasks,
            "action_descriptions": action_descriptions,
        }

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

    def get_all_tasks(self, db_session: Session, user_id: UUID) -> List[Task]:
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
