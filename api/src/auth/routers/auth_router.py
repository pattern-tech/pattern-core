from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.utils.bcrypt_helper import generate_access_token
from src.auth.services.auth_service import (
    AuthService,
    LoginInput,
    RegisterInput,
    VerifyInput
)
from src.util.execptions import *
from src.db.sql_alchemy import Database
from src.util.response import global_response, GlobalResponse, ExceptionResponse

router = APIRouter(prefix="/auth")
database = Database()

auth = AuthService()

# Create a module-level dependency
get_db_dependency = Depends(database.get_db)


class AuthOutput(BaseModel):
    access_token: str


@router.post(
    "/register",
    response_model=GlobalResponse[AuthOutput, dict],
    summary="User Registration",
    description="Register a new user with email and password.",
    deprecated=True,
    responses={
        409: {
            "model": ExceptionResponse,
            "description": "User or Email already exists"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request"
        },
    }
)
def register(input: RegisterInput, db: Session = get_db_dependency):
    """
    Register a new user.

    - **email**: User's email address
    - **password**: User's password
    """
    try:
        user = auth.register(input, db)

        payload = {"id": str(user.id)}
        token = generate_access_token(data=payload)
        return global_response(
            {
                "access_token": token,
            }
        )
    except AlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/login",
    response_model=GlobalResponse[AuthOutput, dict],
    summary="User Login",
    description="Authenticate a user with email and password.",
    deprecated=True,
    responses={
        404: {
            "model": ExceptionResponse,
            "description": "User not found"
        },
        401: {
            "model": ExceptionResponse,
            "description": "Incorrect password"
        },
        400: {
            "model": ExceptionResponse,
            "description": "Bad request"
        },
    }
)
def login(input: LoginInput, db: Session = get_db_dependency):
    """
    Login a user and return an access token.

    - **email**: User's email address
    - **password**: User's password
    """
    try:
        user = auth.authenticate_user(input.email.lower(), input.password, db)

        payload = {"id": str(user.id)}
        token = generate_access_token(data=payload)
        return global_response(
            {
                "access_token": token,
            }
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidPasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/verify",
    response_model=GlobalResponse[AuthOutput, dict],
    summary="Verify a Signature",
    description="Verify a signature according to SIWE spec",
    responses={
        400: {
            "model": ExceptionResponse,
            "description": "Bad request including invalid message or signature"
        },
    }
)
def verify(input: VerifyInput, db: Session = get_db_dependency):
    """
    Verify a signature according to SIWE spec and return an access token

    - **message**: A SIWE message
    - **signature**: User's signature for the message
    """
    try:
        user = auth.verify_signature(
            input.message, input.signature, db)

        payload = {"id": str(user.id)}
        token = generate_access_token(data=payload)
        return global_response(
            {
                "access_token": token,
            }
        )
    except InvalidMessageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
