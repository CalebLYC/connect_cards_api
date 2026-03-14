from typing import Optional, List
from app.models.access_token import AccessToken
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db_utils.postgres_utils import PostgresTableOperations


class AccessTokenRepository:
    def __init__(self, db: AsyncSession):
        self._db_ops = PostgresTableOperations(db, AccessToken)

    async def find_by_id(self, id: str) -> Optional[AccessToken]:
        """Find an access token by its ID.

        Args:
            id (str): ID of the access token to find.

        Returns:
            Optional[AccessToken]: AccessToken object if found, None otherwise.
        """
        doc = await self._db_ops.find_one(
            {"id": id},
        )
        if doc:
            doc.pop("_sa_instance_state", None)
            return AccessToken(**doc)
        return None

    async def find_by_user_and_id(self, id: str, user_id: str) -> Optional[AccessToken]:
        """Find an access token by its ID and user ID.

        Args:
            id (str):  ID of the access token.
            user_id (str): ID of the user whose token should be found.

        Returns:
            Optional[AccessToken]: AccessToken object if found, None otherwise.
        """
        doc = await self._db_ops.find_one(
            {"id": id, "user_id": user_id},
        )
        if doc:
            doc.pop("_sa_instance_state", None)
            return AccessToken(**doc)
        return None

    async def find_by_user_id_and_token(
        self, user_id: str, token: str
    ) -> Optional[AccessToken]:
        """Find an access token by user ID and token string.

        Args:
            user_id (str): ID of the user whose token should be found.
            token (str): The token string to search for.

        Returns:
            Optional[AccessToken]: AccessToken object if found, None otherwise.
        """
        doc = await self._db_ops.find_one(
            {"user_id": user_id, "token": token},
        )
        if doc:
            doc.pop("_sa_instance_state", None)
            return AccessToken(**doc)
        return None

    async def find_by_user_id(self, userid: str) -> List[AccessToken]:
        """Find access tokens by user ID.

        Args:
            userid (str): ID of the user whose tokens should be found.

        Returns:
            List[AccessToken]: List of AccessToken objects associated with the user.
        """
        doc = await self._db_ops.find_one(
            {"user_id": id},
        )
        docs = await self._db_ops.find_many({"user_id": userid}, limit=None)

        tokens = []
        for doc in docs:
            doc.pop("_sa_instance_state", None)
            tokens.append(AccessToken(**doc))
        return tokens

    async def find_by_token(self, token: str) -> Optional[AccessToken]:
        """Find an access token by its token string.

        Args:
            token (str): The token string to search for.

        Returns:
            Optional[AccessToken]: AccessToken object if found, None otherwise.
        """
        doc = await self._db_ops.find_one({"token": token})
        if doc:
            doc.pop("_sa_instance_state", None)
            return AccessToken(**doc)
        return None

    async def list_access_tokens(
        self, skip: int = 0, limit: Optional[int] = 100, all: bool = False
    ) -> List[AccessToken]:
        """List access tokens with optional pagination.

        Args:
            skip (int, optional): Number of access tokens to skip. Defaults to 0.
            limit (Optional[int], optional): Maximum number of access tokens to return. Defaults to 100.
            all (bool, optional): If True, returns all access tokens without pagination. Defaults to False.

        Returns:
            List[AccessToken]: List of AccessToken objects.
        """
        query = {}
        effective_skip = max(0, skip)
        effective_limit = max(1, limit) if limit is not None else 100

        if all:
            docs = await self._db_ops.find_many(query=query, skip=0, limit=None)
        else:
            docs = await self._db_ops.find_many(
                query=query, skip=effective_skip, limit=effective_limit
            )

        tokens = []
        for doc in docs:
            doc.pop("_sa_instance_state", None)
            tokens.append(AccessToken(**doc))
        return tokens

    async def create(self, access_token: AccessToken) -> str:
        """Create a new access token in the database.

        Args:
            access_token (AccessToken): AccessToken object to create.

        Returns:
            str: ID of the created access token.
        """
        token_dict = access_token.__dict__.copy()
        token_dict.pop("_sa_instance_state", None)
        inserted_id = await self._db_ops.insert_one(token_dict)
        return str(inserted_id)

    async def update(self, id: str, update_data: dict) -> bool:
        """Update an access token by ID.

        Args:
            id (str): ID of the access token to update.
            update_data (dict): Dictionary of fields to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        modified_count = await self._db_ops.update_one({"id": id}, update_data)
        return modified_count > 0

    async def delete(self, id: str) -> bool:
        """Delete an access token by ID.

        Args:
            id (str): ID of the access token to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        deleted_count = await self._db_ops.delete_one({"id": id})
        return deleted_count > 0

    async def delete_by_user_id(self, user_id: str) -> bool:
        """Delete access tokens by user ID.

        Args:
            user_id (str): ID of the user whose tokens should be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        deleted_count = await self._db_ops.delete_one({"user_id": user_id})
        return deleted_count > 0

    async def delete_all(self) -> bool:
        """Delete all access tokens in the database.

        Returns:
            bool: True if all access tokens were deleted, False otherwise.
        """
        deleted_count = await self._db_ops.delete_many({})
        return deleted_count > 0
