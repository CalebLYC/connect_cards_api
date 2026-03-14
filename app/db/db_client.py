from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import logging


class PostgresClient:
    def __init__(self, uri: str):
        self.engine = create_async_engine(uri, echo=True)
        self.sessionmaker = async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_session(self):
        """Get a new database session.

        Yields:
            AsyncSession: A new database session.
        """
        try:
            async with self.sessionmaker() as session:
                yield session
        except Exception as e:
            logging.error(f"Error getting DB session: {e}")
            raise

    async def close(self):
        """Close the database engine."""
        try:
            await self.engine.dispose()
        except Exception as e:
            logging.error(f"Error closing DB engine: {e}")
            raise
