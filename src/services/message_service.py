from datetime import datetime
from typing import List

from beanie import SortDirection

from src.models.message_model import Message
from src.models.user_models import User


class MessageService:
    @staticmethod
    async def create_message(
        sender_username: str, receiver_username: str, text: str
    ) -> Message:
        sender = await User.find_one(User.username == sender_username)
        if not sender:
            raise ValueError("Sender not found")

        receiver = await User.find_one(User.username == receiver_username)
        if not receiver:
            raise ValueError("Receiver not found")

        message = Message(
            text=text,
            sender_username=sender_username,
            receiver_username=receiver_username,
            created_at=datetime.utcnow(),
        )
        await message.save()
        return message

    @staticmethod
    async def get_messages(
        sender_username: str, receiver_username: str
    ) -> List[Message]:
        messages = await Message.find(
            (Message.sender_username == sender_username)
            & (Message.receiver_username == receiver_username)
        ).to_list()
        return messages

    @staticmethod
    async def get_last_messages_for_user(
        username: str, limit: int = 20
    ) -> List[Message]:
        messages = await Message.find(
            {"$or": [{"sender_username": username}, {"receiver_username": username}]},
            sort=[("created_at", SortDirection.ASCENDING)],
            limit=limit,
        ).to_list()
        return messages
