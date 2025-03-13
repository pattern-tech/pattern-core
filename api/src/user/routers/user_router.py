from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from src.db.sql_alchemy import Database
from src.auth.utils.get_token import authenticate_user
from src.user.services.user_service import UserService
from src.util.response import global_response, GlobalResponse


router = APIRouter(prefix="/user")
database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_service() -> UserService:
    return UserService()


class CreateUserInput(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True


class UserOutput(BaseModel):
    id: UUID
    email: str
    wallet_address: str
    chain_id: int

    class Config:
        from_attributes = True


@router.get("", response_model=GlobalResponse[UserOutput, dict])
def get_user(
    user_id: UUID = Depends(authenticate_user),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    """
    Retrieves a user by their ID.

    Returns:
        UserOutput: The user data
    """
    try:
        user = service.get_user(db, user_id)
        return global_response(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
