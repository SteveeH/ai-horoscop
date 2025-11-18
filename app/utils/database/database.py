from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure


class DatabaseClient:
    """
    Main class of project database client.
    """

    def __init__(self, connection_string: str, db_name: str) -> None:
        self.mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(connection_string)
        self.database = self.mongo_client[db_name]

    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Get database instance

        :return: database instance
        """
        return self.database

    def close_connection(self) -> bool:
        """
        Closing connection with MongoDB

        :return: bool
        """
        if self.mongo_client.close():
            return True
        return False

    async def check_connection(self) -> bool:
        """
        Check if connection with MongoDB is available

        :return: bool
        """
        try:
            await self.mongo_client.admin.command("ping")
            return True
        except ConnectionFailure:
            return False
