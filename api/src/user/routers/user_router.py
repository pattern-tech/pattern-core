from uuid import UUID
from src.auth.utils.get_token import authenticate_user
from src.db.sql_alchemy import Database
from src.user.services.user_service import UserService
from src.util.response import global_response
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user")
database = Database()
user = UserService()


@router.get("")
def get_user(
    user_id: UUID = Depends(authenticate_user), db: Session = Depends(database.get_db)
):
    """
    Retrieve User for the authenticated user.
    """
    result = user.get_user_by_id(user_id=user_id, db=db)
    return global_response(result)
