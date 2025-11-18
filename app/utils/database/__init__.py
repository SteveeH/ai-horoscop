from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import SERVER_SETTINGS
from app.utils.database.database import DatabaseClient

DB = DatabaseClient(
    connection_string=SERVER_SETTINGS.MONGO_DB_URL,
    db_name=SERVER_SETTINGS.MONGO_DB_NAME,
)
