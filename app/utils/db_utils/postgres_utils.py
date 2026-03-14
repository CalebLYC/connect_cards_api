from typing import Any, Dict, List, Optional
from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db_utils.db_utils import BaseCollectionOperations


class PostgresTableOperations(BaseCollectionOperations[AsyncSession]):
    """
    Concrete implementation of BaseCollectionOperations for PostgreSQL (using SQLAlchemy async).
    """

    def __init__(self, db: AsyncSession, table):
        """
        Initializes PostgresTableOperations for a specific SQLAlchemy table.

        Args:
            db (AsyncSession): The SQLAlchemy async session.
            table: The SQLAlchemy table/model class to operate on.
        """
        super().__init__(db, table.__tablename__)
        self._table = table

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Finds a single document in the table based on the query.

        Args:
            query (Dict[str, Any]): The query to filter the document.

        Returns:
            Optional[Dict[str, Any]]: The found document as a dictionary, or None if not found.
        """
        stmt = select(self._table).filter_by(**query)
        result = await self._db_connection.execute(stmt)
        row = result.scalar_one_or_none()
        return row.__dict__ if row else None

    async def find_many(
        self,
        query: Dict[str, Any] = None,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, Any]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Finds multiple documents in the table based on the query, with optional projection, sorting, skipping, and limiting.

        Args:
            query (Dict[str, Any], optional): The query to filter the documents. Defaults to None.
            projection (Optional[Dict[str, Any]], optional): Projection/Description of fields to return. Defaults to None.
            sort (Optional[Dict[str, Any]], optional): Sorting criteria, e.g., {"field": 1} for ascending or {"field": -1} for descending. Defaults to None.
            skip (Optional[int], optional): Number of documents to skip. Defaults to None.
            limit (Optional[int], optional): Maximum number of documents to return. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of documents as dictionaries that match the query.
        """
        stmt = select(self._table)
        if query:
            stmt = stmt.filter_by(**query)
        if sort:
            for field, direction in sort.items():
                stmt = stmt.order_by(
                    getattr(self._table, field).desc()
                    if direction == -1
                    else getattr(self._table, field).asc()
                )
        if skip:
            stmt = stmt.offset(skip)
        if limit:
            stmt = stmt.limit(limit)
        result = await self._db_connection.execute(stmt)
        rows = result.scalars().all()
        return [row.__dict__ for row in rows]

    async def insert_one(self, document: Dict[str, Any]) -> str:
        """Inserts a single document into the table.

        Args:
            document (Dict[str, Any]): The document to insert, as a dictionary.

        Returns:
            str: The ID of the inserted document as a string.
        """
        stmt = insert(self._table).values(**document).returning(self._table.id)
        result = await self._db_connection.execute(stmt)
        await self._db_connection.commit()
        inserted_id = result.scalar()
        return str(inserted_id)

    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Inserts multiple documents into the table.

        Args:
            documents (List[Dict[str, Any]]): A list of documents to insert, each as a dictionary.

        Returns:
            List[str]: A list of IDs of the inserted documents as strings.
        """
        stmt = insert(self._table).returning(self._table.id)
        result = await self._db_connection.execute(stmt, documents)
        await self._db_connection.commit()
        ids = result.scalars().all()
        return [str(i) for i in ids]

    async def update_one(
        self, query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:
        """Updates a single document in the table based on the query.

        Args:
            query (Dict[str, Any]): The query to filter the document to update.
            update_data (Dict[str, Any]): The data to update the document with, as a dictionary.

        Returns:
            int: The number of rows affected by the update operation.
        """
        stmt = update(self._table).filter_by(**query).values(**update_data)
        result = await self._db_connection.execute(stmt)
        await self._db_connection.commit()
        return result.rowcount

    async def update_many(
        self, query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:
        """Updates multiple documents in the table based on the query.

        Args:
            query (Dict[str, Any]): The query to filter the documents to update.
            update_data (Dict[str, Any]): The data to update the documents with, as a dictionary.

        Returns:
            int: The number of rows affected by the update operation.
        """
        stmt = update(self._table).filter_by(**query).values(**update_data)
        result = await self._db_connection.execute(stmt)
        await self._db_connection.commit()
        return result.rowcount

    async def delete_one(self, query: Dict[str, Any]) -> int:
        """Deletes a single document from the table based on the query.

        Args:
            query (Dict[str, Any]): The query to filter the document to delete.

        Returns:
            int: The number of rows affected by the delete operation.
        """
        stmt = delete(self._table).filter_by(**query)
        result = await self._db_connection.execute(stmt)
        await self._db_connection.commit()
        return result.rowcount

    async def delete_many(self, query: Dict[str, Any] = None) -> int:
        """Deletes multiple documents from the table based on the query.

        Args:
            query (Dict[str, Any], optional): The query to filter the documents to delete. Defaults to None.

        Returns:
            int: The number of rows affected by the delete operation.
        """
        stmt = delete(self._table)
        if query:
            stmt = stmt.filter_by(**query)
        result = await self._db_connection.execute(stmt)
        await self._db_connection.commit()
        return result.rowcount
