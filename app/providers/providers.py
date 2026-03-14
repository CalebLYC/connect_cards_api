from functools import lru_cache
from fastapi import Depends

from app.core.config import Settings
from app.db.db_client import PostgresClient


@lru_cache()
def get_settings():
    """Get the app settings

    Returns:
        Settings: All app settings and configuration params
    """
    return Settings()


async def get_db(settings: Settings = Depends(get_settings)):
    """Get the database session

    Args:
        settings (Settings, optional): App settings. Auto-filled from get_settings dependance.
    Yields:
       AsyncSession: A new database session.
    """
    postgres = PostgresClient(uri=settings.database_uri)
    async for session in postgres.get_session():
        yield session
