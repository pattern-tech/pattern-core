import os
import bcrypt

from jose import JWTError, jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from src.util.exceptions import JWTDecodeError

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the provided plain text password matches the hashed password.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_access_token(data: dict) -> dict:
    """
    Generate a dictionary of user data into a JWT access token.

    Args:
        data (dict): The user data to include in the token payload.

    Returns:
        dict: A dictionary containing the generated access token.
    """
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodes a JWT access token to extract the payload data.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: A dictionary containing the user ID if present.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded_token.get("id")
        if user_id:
            return {"user_id": user_id}
        else:
            raise JWTError("Required fields not found in token")
    except JWTError:
        raise JWTDecodeError("Invalid or expired token")
