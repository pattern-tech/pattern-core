import os
import uuid

from dotenv import load_dotenv
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Table,
    Boolean,
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    create_engine,
)


load_dotenv()

Base = declarative_base()


class ParentBase(Base):
    __abstract__ = True  # Make sure this class is abstract and not mapped to any table

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True)


# Association table for the many-to-many relationship
project_tools_association = Table(
    "project_tools_association",
    Base.metadata,
    Column("project_id", UUID(as_uuid=True),
           ForeignKey("projects.id"), primary_key=True),
    Column("tool_id", UUID(as_uuid=True),
           ForeignKey("tools.id"), primary_key=True)
)


class UserModel(ParentBase):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)

    # Relationships
    workspaces = relationship(
        "Workspace", back_populates="user", cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="user",
                         cascade="all, delete-orphan")
    projects = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )


class Workspace(ParentBase):
    __tablename__ = "workspaces"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="workspaces")
    projects = relationship(
        "Project", back_populates="workspace", cascade="all, delete-orphan"
    )


class Project(ParentBase):
    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    user = relationship("UserModel", back_populates="projects")
    tasks = relationship("Task", back_populates="project",
                         cascade="all, delete-orphan")
    sub_tasks = relationship(
        "SubTask", back_populates="project", cascade="all, delete-orphan"
    )
    task_events = relationship(
        "TaskEvent", back_populates="project", cascade="all, delete-orphan"
    )
    sub_task_tools = relationship(
        "SubTaskTool", back_populates="project", cascade="all, delete-orphan"
    )
    task_usages = relationship(
        "TaskUsage", back_populates="project", cascade="all, delete-orphan"
    )
    sub_task_objects = relationship(
        "SubTaskObject", back_populates="project", cascade="all, delete-orphan"
    )

    # Many-to-Many Relationship with Tools
    tools = relationship(
        "Tool",
        secondary=project_tools_association,
        back_populates="projects",
        lazy="dynamic"
    )


class Task(ParentBase):
    __tablename__ = "tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    project_id = Column(UUID(as_uuid=True), ForeignKey(
        "projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False)
    name = Column(String, nullable=True)
    task = Column(String, nullable=False)
    status = Column(String, nullable=False)
    response = Column(Text, nullable=True)
    extra_data = Column(JSONB, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    user = relationship("UserModel", back_populates="tasks")
    sub_tasks = relationship(
        "SubTask", back_populates="task", cascade="all, delete-orphan"
    )
    task_events = relationship(
        "TaskEvent", back_populates="task", cascade="all, delete-orphan"
    )
    sub_task_tools = relationship(
        "SubTaskTool", back_populates="task", cascade="all, delete-orphan"
    )
    task_usages = relationship(
        "TaskUsage", back_populates="task", cascade="all, delete-orphan"
    )
    sub_task_objects = relationship(
        "SubTaskObject", back_populates="task", cascade="all, delete-orphan"
    )


class SubTask(ParentBase):
    __tablename__ = "sub_tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    task_id = Column(UUID(as_uuid=True), ForeignKey(
        "tasks.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey(
        "projects.id"), nullable=False)
    name = Column(String, nullable=True)
    sub_task = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(Integer, nullable=True)
    order = Column(Integer, nullable=True)
    response = Column(Text, nullable=True)
    extra_data = Column(JSONB, nullable=True)

    # Relationships
    task = relationship("Task", back_populates="sub_tasks")
    project = relationship("Project", back_populates="sub_tasks")
    task_events = relationship(
        "TaskEvent", back_populates="sub_task", cascade="all, delete-orphan"
    )
    sub_task_tools = relationship(
        "SubTaskTool", back_populates="sub_task", cascade="all, delete-orphan"
    )
    task_usages = relationship(
        "TaskUsage", back_populates="sub_task", cascade="all, delete-orphan"
    )
    sub_task_objects = relationship(
        "SubTaskObject", back_populates="sub_task", cascade="all, delete-orphan"
    )


class TaskEvent(ParentBase):
    __tablename__ = "task_events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    project_id = Column(UUID(as_uuid=True), ForeignKey(
        "projects.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    sub_task_id = Column(UUID(as_uuid=True), ForeignKey(
        "sub_tasks.id"), nullable=True)
    type = Column(String, nullable=False)
    info = Column(String, nullable=True)
    input = Column(String, nullable=True)
    extra_data = Column(JSONB, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="task_events")
    task = relationship("Task", back_populates="task_events")
    sub_task = relationship("SubTask", back_populates="task_events")


class SubTaskTool(ParentBase):
    __tablename__ = "sub_task_tools"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    sub_task_id = Column(UUID(as_uuid=True), ForeignKey(
        "sub_tasks.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey(
        "projects.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey(
        "tasks.id"), nullable=False)
    tool_id = Column(UUID(as_uuid=True), ForeignKey(
        "tools.id"), nullable=False)
    status = Column(String, nullable=False)
    response = Column(Text, nullable=True)
    score = Column(Integer, nullable=False)

    # Relationships
    sub_task = relationship("SubTask", back_populates="sub_task_tools")
    project = relationship("Project", back_populates="sub_task_tools")
    task = relationship("Task", back_populates="sub_task_tools")
    tool = relationship("Tool", back_populates="sub_task_tools")


class Tool(ParentBase):
    __tablename__ = "tools"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    vector_id = Column(String, nullable=True)
    function_name = Column(String, nullable=True, unique=True)
    extra_data = Column(JSONB, nullable=True)
    api_key = Column(String, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    sub_task_tools = relationship(
        "SubTaskTool", back_populates="tool", cascade="all, delete-orphan"
    )

    # Many-to-Many Relationship with Projects
    projects = relationship(
        "Project",
        secondary=project_tools_association,
        back_populates="tools",
        lazy="dynamic"
    )


class TaskUsage(ParentBase):
    __tablename__ = "task_usages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    project_id = Column(UUID(as_uuid=True), ForeignKey(
        "projects.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    sub_task_id = Column(UUID(as_uuid=True), ForeignKey(
        "sub_tasks.id"), nullable=True)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    total_token = Column(Integer, nullable=False)
    input_token = Column(Integer, nullable=False)
    output_token = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    extra_data = Column(JSONB, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="task_usages")
    task = relationship("Task", back_populates="task_usages")
    sub_task = relationship("SubTask", back_populates="task_usages")


class SubTaskObject(ParentBase):
    __tablename__ = "sub_task_objects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    sub_task_id = Column(UUID(as_uuid=True), ForeignKey(
        "sub_tasks.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey(
        "projects.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey(
        "tasks.id"), nullable=False)
    object_key = Column(String, nullable=False)
    source = Column(String, nullable=False)

    # Relationships
    sub_task = relationship("SubTask", back_populates="sub_task_objects")
    project = relationship("Project", back_populates="sub_task_objects")
    task = relationship("Task", back_populates="sub_task_objects")


def init_db():
    username = os.environ.get("POSTGRES_USERNAME")
    password = os.environ.get("POSTGRES_PASSWORD")
    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")
    database = os.environ.get("POSTGRES_DB")
    DATABASE_URL = (
        f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
    )
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
