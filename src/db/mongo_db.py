import logging

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.settings import settings
from src.models.user_models import User


async def connect_to_mongodb() -> None:
    logging.info("Connect to database..")
    db_client = AsyncIOMotorClient(settings.mongo_url)[settings.MONGO_DB]
    await init_beanie(
        database=db_client,
        document_models=[
            User
        ]
    )
    logging.info("Connected to database")
