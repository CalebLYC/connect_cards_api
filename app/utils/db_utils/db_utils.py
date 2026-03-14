from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic


# Define a TypeVar for the database connection type
DBConnection = TypeVar("DBConnection")


class BaseCollectionOperations(ABC, Generic[DBConnection]):
    """
    Abstract Base Class for generic CRUD operations on a collection/table.
    Repositories should depend on this abstract interface.
    It is generic over the type of the database connection (DBConnection).
    All return types are now generic and database-agnostic.
    """

    def __init__(self, db_connection: DBConnection, collection_or_table_name: str):
        """
        Initializes the base operations with a database connection and target name.

        Args:
            db_connection (DBConnection): The specific database connection object.
            collection_or_table_name (str): The name of the collection or table to operate on.
        """
        self._db_connection = db_connection
        self._collection_or_table_name = collection_or_table_name

    @abstractmethod
    async def find_one(
        self,
        query: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Abstract method to find a single document/row."""
        pass

    @abstractmethod
    async def find_many(
        self,
        query: Dict[str, Any] = None,
        projection: Optional[Dict[str, Any]] = None,  # Fields to return
        sort: Optional[Dict[str, Any]] = None,  # Sorting order
        skip: Optional[int] = None,  # Number of documents to skip
        limit: Optional[int] = None,  # Maximum number of documents to return
    ) -> List[Dict[str, Any]]:
        """Abstract method to find multiple documents/rows. Should return a list of documents."""
        pass

    @abstractmethod
    async def insert_one(
        self, document: Dict[str, Any]
    ) -> str:  # Returns inserted ID as string
        """Abstract method to insert a single document/row, returning its ID as a string."""
        pass

    @abstractmethod
    async def insert_many(
        self, documents: List[Dict[str, Any]]
    ) -> List[str]:  # Returns list of inserted IDs as strings
        """Abstract method to insert multiple documents/rows, returning their IDs as strings."""
        pass

    @abstractmethod
    async def update_one(
        self, query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:  # Returns count of modified documents
        """Abstract method to update a single document/row, returning the number of modified documents."""
        pass

    @abstractmethod
    async def update_many(
        self, query: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:  # Returns count of modified documents
        """Abstract method to update multiple documents/rows, returning the number of modified documents."""
        pass

    @abstractmethod
    async def delete_one(
        self, query: Dict[str, Any]
    ) -> int:  # Returns count of deleted documents
        """Abstract method to delete a single document/row, returning the number of deleted documents."""
        pass

    @abstractmethod
    async def delete_many(
        self, query: Dict[str, Any] = None
    ) -> int:  # Returns count of deleted documents
        """Abstract method to delete multiple documents/rows, returning the number of deleted documents."""
        pass
