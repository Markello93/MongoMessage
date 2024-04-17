from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class Message(Document):
    message_id: UUID = Field(default_factory=uuid4)
    text: str
    sender_username: str
    receiver_username: str
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "messages"
