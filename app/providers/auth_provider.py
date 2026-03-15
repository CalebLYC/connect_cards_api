from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.jwt import JWTUtils
from app.providers.service_providers import  get_user_service
from app.repositories.access_token_repository import AccessTokenRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.providers.repository_providers import get_access_token_repository, get_user_repository
from app.services.auth.user_service import UserService


oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_token(
    token: str = Depends(oauth_2_scheme),
    access_token_repos: AccessTokenRepository = Depends(get_access_token_repository),
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
        db_token = await access_token_repos.find_by_token(token=token)
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid token")
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


def require_permission(permission_code: str) -> Depends:
    try:

        async def dependency(
            user: User = Depends(auth_middleware),
            ps: UserService = Depends(get_user_service),
        ):
            try:
                if user.is_superuser():
                    return True
                
                await ps.ensure_permission(
                    user=user,
                    permission_code=permission_code,
                )
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error ensuring permission: {str(e)}",
                )

        return Depends(dependency)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while setting permission dependency: {str(e)}",
        )


def require_role(role_name: str) -> Depends:
    try:

        async def dependency(
            user: User = Depends(auth_middleware),
            rs: UserService = Depends(get_user_service),
        ):
            try:
                if user.is_superuser():
                    return True
                
                await rs.ensure_role(
                    user=user, role_name=role_name
                )
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error ensuring role: {str(e)}",
                )

        return Depends(dependency)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while setting permission dependency: {str(e)}",
        )