from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth.utils.bcrypt_helper import decode_access_token

security = HTTPBearer()


def get_jwt_token(request: Request):
    """
    Extract the JWT token from the Authorization header of the HTTP request.

    Parameters:
        request (Request): The incoming HTTP request object.

    Returns:
        str: The JWT token extracted from the Authorization header.

    Raises:
        HTTPException: If the Authorization header is missing or invalid.
    """
    authorization: str = request.headers.get("Authorization")
    if authorization:
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() == "bearer":
            return param
    raise HTTPException(
        status_code=401,
        detail="Not authenticated",
    )


def authenticate_user(
    request: Request, authorization: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Authenticate the user by decoding the JWT token and extracting the user ID.

    Parameters:
        request (Request): The incoming HTTP request object.
        authorization (HTTPAuthorizationCredentials): The bearer token credentials,
                                                      automatically provided by FastAPI dependency injection.

    Returns:
        str: The user ID extracted from the decoded JWT token.

    Raises:
        HTTPException: If the token is missing or invalid.
    """
    token: str = ""
    if authorization:
        token = authorization.credentials
    else:
        token = get_jwt_token(request)
    decode_token = decode_access_token(token)
    return decode_token["user_id"]
