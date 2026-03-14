from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.jwt import JWTUtils
from app.db.repositories.user_repository import UserRepository
from app.models.user import User
from app.providers.repository_providers import get_user_repository


oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_token(
    token: str = Depends(oauth_2_scheme),
    # access_token_repos: AccessTokenRepository = Depends(get_access_token_repository),
) -> str:
    """Verify a token by decoding it and verify the existence of the user ID

    Args
        token(str): The token string. Auto-filled by oauth_2_scheme which get it from the request headers

    Raises:
        HTTPException: 401 if the token is invalid
        HTTPException: 401 if the token is invalid because the got User Id is invalide

    Returns:
        str: ID of the authenticated user
    """
    try:
        payload = JWTUtils.decode_access_token(token=token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        """access_token = await access_token_repos.find_by_token_and_user_id(
            user_id=user_id, token=token
        )
        if not access_token:
            raise HTTPException(status_code=401, detail="Expired")"""
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def auth_middleware(
    user_id: str = Depends(verify_token),
    user_repos: UserRepository = Depends(get_user_repository),
) -> User:
    """Authentification middleware to get the user from the token.

    Args:
        user_id (str, optional): ID of the user. Auto-filled by the verify_token dependency. Defaults to Depends(verify_token).
        user_repos (UserRepository, optional): User repository. Auto-filled by the get_user_repository dependency. Defaults to Depends(get_user_repository).

    Raises:
        HTTPException: 401 if the user is not found
        e: Exception that can be raised by the user repository
        HTTPException: 500 if an error occurs

    Returns:
        User: The user object
    """
    try:
        # print(user_id)
        user = await user_repos.find_by_id(id=user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user by token: {str(e)}",
        )
