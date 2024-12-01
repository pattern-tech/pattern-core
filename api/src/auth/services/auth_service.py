from fastapi import HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from src.workspace.services.workspace_service import WorkspaceService
from src.auth.utils.bcrypt_helper import hash_password, verify_password
from src.db.models import UserModel
from src.db.sql_alchemy import Database

database = Database()


class RegisterInput(BaseModel):
    email: EmailStr = Field(
        ..., example="user@example.com", description="The email address of the user"
    )
    password: str = Field(
        ...,
        example="securepassword123",
        description="The password for the user account",
    )


class LoginInput(BaseModel):
    email: EmailStr = Field(
        ..., example="user@example.com", description="The email address of the user"
    )
    password: str = Field(
        ...,
        example="securepassword123",
        description="The password for the user account",
    )


class AuthService:
    """
    Service class for handling user authentication and registration logic.
    """

    def __init__(self):
        self.workspace = WorkspaceService()

    def register(self, input: RegisterInput, db: Session) -> str:
        """
        Registers a new user by saving their details into the database.

        Args:
            input (RegisterInput): The registration input containing email and password.
            db (Session): The database session for executing queries.

        Returns:
            str: Success message indicating the user was registered.

        Raises:
            HTTPException: If a user with the same email already exists.
        """
        # Check if the user already exists
        existing_user = db.query(UserModel).filter_by(email=input.email.lower()).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Hash the user's password and create a new user record
        hashed_password = hash_password(input.password)
        new_user = UserModel(email=input.email.lower(), password=hashed_password)
        db.add(new_user)
        db.commit()

        self.workspace.create_workspace(db, "Default", new_user.id)

        return new_user

    def authenticate_user(self, email: str, password: str, db: Session):
        """
        Authenticates a user by verifying their email and password.

        Args:
            email (str): The user's email address.
            password (str): The user's plaintext password.
            db (Session): The database session for executing queries.

        Returns:
            UserModel: The authenticated user object if authentication is successful.
            bool: `False` if authentication fails.
        """
        # Fetch the user from the database using the provided email
        user = db.query(UserModel).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        # Verify the provided password matches the stored hash
        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        return user
