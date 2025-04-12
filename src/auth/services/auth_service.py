from typing import Optional
from siwe import SiweMessage
from fastapi import HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from src.util.exceptions import *
from src.db.models import UserModel
from src.db.sql_alchemy import Database
from src.share.base_types import WalletAddress
from src.user.services.user_service import UserService
from src.workspace.services.workspace_service import WorkspaceService
from src.auth.utils.bcrypt_helper import hash_password, verify_password

database = Database()


class RegisterInput(BaseModel):
    email: Optional[EmailStr] = Field(
        None, example="user@example.com", description="The email address of the user"
    )
    password: Optional[str] = Field(
        None, example="securepassword123", description="The password for the user account"
    )
    wallet_address: WalletAddress = Field(
        ...,
        example="0x0...",
        description="The wallet address of the user"
    )
    chain_id: int = Field(
        ...,
        example="1",
        description="The chain id of the user"
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


class VerifyInput(BaseModel):
    message: str = Field(
        ..., example="0x0...", description="The SIWE message"
    )
    signature: str = Field(
        ..., example="0x0...", description="User's signature for a message"
    )


class AuthService:
    """
    Service class for handling user authentication and registration logic.
    """

    def __init__(self):
        self.workspace_service = WorkspaceService()
        self.user_service = UserService()

    def register(self, input: RegisterInput, db: Session) -> str:
        """
        Registers a new user by saving their details into the database.

        Args:
            input (RegisterInput): The registration input .
            db (Session): The database session for executing queries.

        Returns:
            str: Success message indicating the user was registered.

        Raises:
            HTTPException: If a user with the same wallet_address already exists.
        """
        # Check if the user already exists
        existing_user = db.query(UserModel).filter_by(
            wallet_address=input.wallet_address).first()
        if existing_user:
            raise AlreadyExistsError("User already exists")

        # # Create a new user record
        if input.email and input.password:
            existing_user = db.query(UserModel).filter_by(
                email=input.email.lower()).first()
            if existing_user:
                raise AlreadyExistsError("This email is already exists")

        if input.password:
            input.password = hash_password(input.password)

        new_user = self.user_service.create_user(
            db, input.wallet_address, input.chain_id, input.email, input.password, )

        self.workspace_service.create_workspace(db, "Default", new_user.id)

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
            raise NotFoundError("User not found with this email")

        # Verify the provided password matches the stored hash
        if not verify_password(password, user.password):
            raise InvalidPasswordError("Incorrect email or password")

        return user

    def verify_signature(self, message: str, signature: str, db: Session):
        """
        Verify a signature according to SIWE spec

        Args:
            message (str): A SIWE message
            signature (str): User's signature for the message

        Returns:
            VerificationResult: The result of the verification, containing the address and chain id of the signing wallet

        Raises:
            HTTPException: If message cannot be parsed or verified
        """
        try:
            siwe_message = SiweMessage.from_message(message)
            siwe_message.verify(signature)
        except ValueError:
            # ValueError is raised if message is invalid according to SIWE
            raise InvalidMessageError(
                "The provided message is not a valid SIWE message")
        except:
            raise InvalidSignatureError("Signature is not valid")

        # check if not exist create new user
        user = self.user_service.get_user_by_wallet_address(
            siwe_message.address, db)
        if not user:
            user = self.register(RegisterInput(
                email=None,
                password=None,
                wallet_address=siwe_message.address,
                chain_id=siwe_message.chain_id
            ), db)

        return user
