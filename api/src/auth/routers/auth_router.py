from src.auth.utils.bcrypt_helper import generate_access_token
from src.auth.services.auth_service import (
    AuthService,
    LoginInput,
    RegisterInput,
)
from src.db.sql_alchemy import Database
from src.util.response import global_response
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth")
database = Database()

auth = AuthService()


@router.post(
    "/register",
    summary="User Registration",
    description="Register a new user with email and password.",
)
def register(input: RegisterInput, db: Session = Depends(database.get_db)):
    """
    Register a new user.

    - **email**: User's email address
    - **password**: User's password
    """
    result = auth.register(input, db)
    return global_response(result)


@router.post(
    "/login",
    summary="User Login",
    description="Authenticate a user with email and password.",
)
def login(input: LoginInput, db: Session = Depends(database.get_db)):
    """
    Login a user and return an access token.

    - **email**: User's email address
    - **password**: User's password
    """
    user = auth.authenticate_user(input.email.lower(), input.password, db)

    payload = {"id": str(user.id)}
    token = generate_access_token(data=payload)
    return global_response(
        {
            "access_token": token,
        }
    )
