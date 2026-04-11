from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None


def get_mongo_db() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("MongoDB client is not initialised — call connect_mongo() first")
    return _client[settings.mongodb_db_name]


async def connect_mongo() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.mongodb_url)


async def close_mongo() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None