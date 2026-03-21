import datetime

from fastapi import HTTPException, status
from app.core.jwt import JWTUtils
from app.core.security import SecurityUtils
from app.repositories.access_token_repository import AccessTokenRepository
from app.repositories.user_repository import UserRepository
from app.models.access_token import AccessToken
from app.schemas.access_token_schema import AccessTokenReadSchema
from app.schemas.auth_schema import (
    ChangeUserPasswordSchema,
    LazyLoginResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    RegisterSchema,
)
from app.models.user import User
from app.schemas.user_schema import LazyUserReadSchema, UserReadSchema, UserUpdateSchema


class AuthService:
    def __init__(
        self,
        access_token_repos: AccessTokenRepository,
        user_repos: UserRepository,
        organization_repos: OrganizationRepository,
    ):
        self.access_token_repos = access_token_repos
        self.user_repos = user_repos
        self.organization_repos = organization_repos

    async def generate_access_token(
        self, user_id: str, expires_in_minutes: int | None = None
    ) -> str:
        """Generate an access token for the user.

        Args:
            user_id (str): The ID of the user for whom to generate the token.
            expires_in_minutes (int | None, optional): The expiration time in minutes. If None, the token will not expire.

        Returns:
            str: The ID of the generated access token.
        """
        expire = None
        if expires_in_minutes:
            expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                minutes=expires_in_minutes
            )
        payload = {
            "sub": str(user_id),
            "exp": expire if expire else None,
            "iat": datetime.datetime.now(datetime.timezone.utc),
        }
        token, expires_at = JWTUtils.create_access_token(
            data=payload, expires_delta=expire if expire else None
        )
        token_doc = AccessToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            revoked=False,
        )
        db_token = await self.access_token_repos.create(access_token=token_doc)
        return db_token.id

    async def revoke_access_token(self, token: str) -> bool:
        """Revoke an access token.

        Args:
            token (str): The access token string to revoke.

        Raises:
            HTTPException: 404 If the token is not found.
            HTTPException: 400 If the token is already revoked.

        Returns:
            bool: True if the token was successfully revoked, otherwise False.
        """
        token_doc = await self.access_token_repos.find_by_token(token=token)
        if not token_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
            )
        if token_doc.revoked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token already revoked"
            )
        return await self.access_token_repos.revoke(id=token_doc.id)

    async def generate_and_get_access_token(
        self, user_id: str, expires_in_minutes: int | None = None
    ) -> AccessToken:
        """Generate an access token and retrieve it.

        Args:
            user_id (str): The ID of the user for whom to generate the token.
            expires_in_minutes (int | None, optional): The expiration time in minutes. If None, the token will not expire.

        Returns:
            AccessToken: The generated access token document.
        """
        token_id = await self.generate_access_token(
            user_id=user_id, expires_in_minutes=expires_in_minutes
        )
        return await self.access_token_repos.find_by_id(id=token_id)

    async def login(self, user: LoginRequestSchema) -> LoginResponseSchema:
        """Login a user and return an access token.

        Args:
            user (LoginRequestSchema): The user credentials for login.

        Raises:
            HTTPException: 404 If the user is not found.
            HTTPException: 401 If the credentials are incorrect.

        Returns:
            LoginResponseSchema: The login response containing the access token and user data.
        """
        db_user = await self.user_repos.find_by_email_with_roles_and_permissions(
            email=user.email
        )
        if not db_user:
            raise HTTPException(status_code=404, detail="Wrong credentials")
        is_auth = SecurityUtils.verify_password(
            hashed=db_user.password, plain=user.password
        )
        if not is_auth:
            raise HTTPException(status_code=401, detail="Wrong credentials")
        token_id = await self.generate_access_token(user_id=db_user.id)
        access_token = await self.access_token_repos.find_by_id(id=token_id)
        return_user = UserReadSchema.model_validate(db_user)
        return_access_token = AccessTokenReadSchema.model_validate(access_token)
        return LoginResponseSchema(access_token=return_access_token, user=return_user)

    async def register(self, user: RegisterSchema) -> LazyLoginResponseSchema:
        """Register a new user and return an access token.

        Args:
            user (RegisterSchema): The user data for registration.

        Raises:
            HTTPException: 400 If the email is already registered.

        Returns:
            LazyLoginResponseSchema: The login response containing the access token and user data.
        """
        if user.password_confirmation:
            if user.password != user.password_confirmation:
                raise HTTPException(
                    status_code=400, detail="Password not match password confirmation"
                )

        if user.organization_id:
            organization = await self.organization_repos.find_by_id(
                user.organization_id
            )
            if not organization:
                raise HTTPException(status_code=404, detail="Organization not found")

        existing = await self.user_repos.find_by_email(user.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password before saving
        hashed_password = SecurityUtils.hash_password(user.password)
        user_doc = User(
            **user.model_dump(
                exclude=[
                    "id",
                    "password_confirmation",
                ]
            )
        )
        user_doc.password = hashed_password
        inserted_user = await self.user_repos.create(user_doc)
        db_user = await self.user_repos.find_by_id(id=inserted_user.id)
        token_id = await self.generate_access_token(user_id=db_user.id)
        access_token = await self.access_token_repos.find_by_id(id=token_id)
        return_user = LazyUserReadSchema.model_validate(db_user)
        return LazyLoginResponseSchema(access_token=access_token, user=return_user)

    async def logout(self, user_id: str) -> None:
        """Logout a user by deleting their access token.

        Args:
            user_id (str): The ID of the user to logout.

        Raises:
            HTTPException: 404 If the user is not found.
            HTTPException: 500 If the logout operation fails.

        Returns:
            LoginResponseSchema: The login response containing the access token and user data.
        """
        await self.access_token_repos.delete_by_user_id(user_id=user_id)

    async def update_user(
        self,
        user: User,
        user_update: UserUpdateSchema,
        logout: bool = False,
    ) -> LazyUserReadSchema:
        """Update a user's information.

        Args:
            user (User): The user object to update.
            user_update (UserUpdateSchema): The user data to update.
            logout (bool, optional):    If True, logout the user after updating. Defaults to False.

        Raises:
            HTTPException: 404 If the user is not found.
            HTTPException: 400 If the email is already registered.
            HTTPException: 500 If the update operation fails.

        Returns:
            LazyUserReadSchema: The updated user data.
        """
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user.id

        if user_update.organization_id:
            organization = await self.organization_repos.find_by_id(
                user_update.organization_id
            )
            if not organization:
                raise HTTPException(status_code=404, detail="Organization not found")

        update_data = user_update.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing = await self.user_repos.find_by_email(update_data["email"])
            if existing and str(existing.id) != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        if "password" in update_data:
            update_data["password"] = SecurityUtils.hash_password(
                update_data.pop("password")
            )
            if logout:
                await self.logout(user_id=user_id)

        for key, value in update_data.items():
            setattr(user, key, value)
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(status_code=500, detail="Update failed")
        return UserReadSchema.model_validate(updated)

    async def change_password(
        self,
        user: User,
        user_update: ChangeUserPasswordSchema,
        logout: bool = True,
    ) -> LazyLoginResponseSchema:
        """Change a user's password.

        Args:
            user (User): The user object whose password is to be changed.
            user_update (ChangeUserPasswordSchema): The user data containing the old and new passwords.
            logout (bool, optional): If True, logout the user after changing the password. Defaults to True.

        Raises:
            HTTPException: 404 If the user is not found.
            HTTPException: 400 If the new password does not match the confirmation.
            HTTPException: 401 If the old password is incorrect.
            HTTPException: 500 If the update operation fails.

        Returns:
            LazyLoginResponseSchema: The updated user data after changing the password.
        """
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user.id

        update_data = user_update.model_dump(exclude_unset=True)

        is_auth = SecurityUtils.verify_password(
            hashed=user.password, plain=user_update.old_password
        )
        if not is_auth:
            raise HTTPException(status_code=401, detail="Wrong credentials")

        if "new_password_confirmation" in update_data:
            if user_update.new_password_confirmation != user_update.new_password:
                raise HTTPException(
                    status_code=400, detail="Password not match password confirmation"
                )

        final_update_data = {}
        final_update_data["password"] = SecurityUtils.hash_password(
            update_data.pop(
                "new_password",
            )
        )

        for key, value in final_update_data.items():
            setattr(user, key, value)
        updated = await self.user_repos.update(user)
        if not updated:
            raise HTTPException(status_code=500, detail="Update failed")

        if logout:
            await self.logout(user_id=user_id)

        # updated = await self.user_repos.find_by_id(user_id)
        token_id = await self.generate_access_token(user_id=user_id)
        access_token = await self.access_token_repos.find_by_id(id=token_id)
        return_user = LazyUserReadSchema.model_validate(updated)
        return LazyLoginResponseSchema(access_token=access_token, user=return_user)

    def generate_random_password(self, length: int = 12) -> str:
        """Generate a random password.

        Args:
            length (int, optional): The length of the password to generate. Defaults to 12.

        Returns:
            str: A randomly generated password.
        """
        return SecurityUtils.generate_random_password(length=length)

    """async def clean_expired_tokens(self):
        await self.access_token_repos.delete_expired_tokens()"""

    """async def clean_expired_tokens():
        await mongo_db["access_tokens"].delete_many({"expires_at": {"$lt": datetime.utcnow()}})"""
