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
    projects = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )

    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
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

    # One-to-Many Relationship with Conversations
    conversations = relationship(
        "Conversation",
        back_populates="project",
        cascade="all, delete-orphan"
    )


class Conversation(ParentBase):
    __tablename__ = "conversations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey(
        "projects.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="conversations")
    user = relationship("UserModel", back_populates="conversations")


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
