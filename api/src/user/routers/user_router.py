from uuid import UUID
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from src.db.sql_alchemy import Database
from src.util.response import global_response
from src.user.services.user_service import UserService
from src.user.repositories.user_repository import UserRepository

router = APIRouter(prefix="/user")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_service() -> UserService:
    repository = UserRepository()
    return UserService(repository)


class CreateUserInput(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True


class UserOutput(BaseModel):
    id: UUID
    email: str

    class Config:
        orm_mode = True


@router.post("", response_model=UserOutput)
def create_user(
    input: CreateUserInput,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    """
    Creates a new user.

    Args:
        input (CreateUserInput): The user creation input
        db (Session): SQLAlchemy session
        service (UserService): User service instance

    Returns:
        UserOutput: The created user data
    """
    try:
        user = service.create_user(db, input.email, input.password)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserOutput)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    """
    Retrieves a user by their ID.

    Args:
        user_id (UUID): The user ID
        db (Session): SQLAlchemy session
        service (UserService): User service instance

    Returns:
        UserOutput: The user data
    """
    try:
        user = service.get_user(db, user_id)
        return global_response(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[UserOutput])
def list_users(
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    """
    Lists all users.

    Args:
        db (Session): SQLAlchemy session
        service (UserService): User service instance

    Returns:
        List[UserOutput]: List of all users
    """
    users = service.list_users(db)
    return global_response(users)


@router.put("/{user_id}", response_model=UserOutput)
def update_user(
    user_id: UUID,
    input: CreateUserInput,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    """
    Updates an existing user by their ID.

    Args:
        user_id (UUID): The user ID
        input (CreateUserInput): Updated user data
        db (Session): SQLAlchemy session
        service (UserService): User service instance

    Returns:
        UserOutput: The updated user data
    """
    try:
        updated_user = service.update_user(db, user_id, input.model_dump())
        return global_response(updated_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    """
    Deletes a user by their ID.

    Args:
        user_id (UUID): The user ID
        db (Session): SQLAlchemy session
        service (UserService): User service instance

    Returns:
        None
    """
    try:
        deleted_user = service.delete_user(db, user_id)
        return global_response(deleted_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
