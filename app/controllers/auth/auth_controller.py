from fastapi import APIRouter, Depends, status

from app.providers.auth_provider import auth_middleware
from app.models.user import User
from app.providers.service_providers import get_auth_service
from app.schemas.auth_schema import (
    ChangeUserPasswordSchema,
    LazyLoginResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    RegisterSchema,
    #ResetUserPasswordSchema,
)
from app.schemas.user_schema import LazyUserReadSchema, UserReadSchema, UserUpdateSchema
from app.services.auth.auth_service import AuthService
from app.utils.constants import http_status


# Router
router = APIRouter(
    tags=["Auth"],
    dependencies=[],
    responses=http_status.router_responses,
)


@router.post(
    "/login",
    response_model=LoginResponseSchema,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    response_description="Login user",
)
async def login(
    user: LoginRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    """Login a user and return authentication tokens.

    Args:
        user (LoginRequestSchema): The login request data, validated against the LoginRequestSchema.
        service (AuthService, optional): Auth service dependency.

    Returns:
        LoginResponseSchema: The login response data containing authentication tokens, validated against the LoginResponseSchema.
    """
    return await service.login(user=user)


@router.post(
    "/register",
    response_model=LazyLoginResponseSchema,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    response_description="Register user",
)
async def register(
    user: RegisterSchema,
    service: AuthService = Depends(get_auth_service),
):
    """Register a new user and return authentication tokens.

    Args:
        user (RegisterSchema): The registration data, validated against the RegisterSchema.
        service (AuthService, optional): Auth service dependency.

    Returns:
        LoginResponseSchema: The registration response data containing authentication tokens, validated against the LoginResponseSchema.
    """
    return await service.register(user=user)


@router.get(
    "/me",
    response_model=UserReadSchema,
    summary="Get the current authenticated user",
)
async def get_user(
    current_user: User = Depends(auth_middleware),
):
    """Get the current authenticated user.

    Args:
        current_user (User, optional): The current user from the authentication middleware.

    Returns:
        UserReadSchema: The current user's data validated against the UserReadSchema.
    """
    return UserReadSchema.model_validate(current_user)


@router.delete(
    "/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Logout the current user"
)
async def logout(
    service: AuthService = Depends(get_auth_service),
    current_user: UserReadSchema = Depends(auth_middleware),
):
    """Logout the current authenticated user.

    Args:
        service (AuthService, optional): Auth service dependency.
        current_user (UserReadSchema, optional): The current user from the authentication middleware.

    Returns:
        Bool: A confirmation message indicating the user was logged out.
    """
    await service.logout(user_id=current_user.id)


"""@router.patch(
    "/me/password/reset",
    response_model=LazyLoginResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Reset a user password.",
)
async def reset_user_password(
    user_request: ResetUserPasswordSchema,
    service: AuthService = Depends(get_auth_service),
    logout: bool = False,
):
    Reset a user's password.

    Args:
        user_request (ResetUserPasswordSchema): The password reset request data, validated against the ResetUserPasswordSchema.
        service (AuthService, optional): Auth service dependency.
        logout (bool, optional): Whether to log out the user after resetting the password. Defaults to False.

    Returns:
        LoginResponseSchema: The login response data containing authentication tokens, validated against the LoginResponseSchema.
    
    return await service.reset_user_password(user_request=user_request, logout=logout)"""


@router.put(
    "/me/update", response_model=LazyUserReadSchema, summary="Update the current user"
)
async def update_user(
    current_user: User = Depends(auth_middleware),
    user_update: UserUpdateSchema = ...,
    service: AuthService = Depends(get_auth_service),
    logout: bool = False,
):
    """Update the current authenticated user.

    Args:
        current_user (User, optional): The current user from the authentication middleware.
        user_update (UserUpdateSchema, optional): The user data to update, validated against the UserUpdateSchema.
        service (AuthService, optional): Auth service dependency.
        logout (bool, optional): Whether to log out the user after updating. Defaults to False.

    Returns:
        _type_: UserReadSchema: The updated user's data validated against the UserReadSchema.
    """
    return await service.update_user(current_user, user_update, logout=logout)


@router.patch(
    "/me/password/update",
    response_model=LazyLoginResponseSchema,
    summary="Change the current user password",
)
async def update_user_password(
    current_user: User = Depends(auth_middleware),
    user_update: ChangeUserPasswordSchema = ...,
    service: AuthService = Depends(get_auth_service),
    logout: bool = True,
):
    """Change the current authenticated user's password.

    Args:
        current_user (User, optional): The current user from the authentication middleware.
        user_update (ChangeUserPasswordSchema, optional): The password change request data, validated against the ChangeUserPasswordSchema.
        service (AuthService, optional): Auth service dependency.
        logout (bool, optional): Whether to log out the user after changing the password. Defaults to True.

    Returns:
        LoginResponseSchema: The login response data containing authentication tokens, validated against the LoginResponseSchema.
    """
    return await service.change_password(current_user, user_update, logout=logout)
