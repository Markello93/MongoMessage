from datetime import datetime

from fastapi import (
    WebSocket,
    WebSocketException,
    status,
    Query,
)
from typing import Annotated

from starlette.exceptions import HTTPException

from src.api.schemas.message_schema import SendMessage
from src.services.message_service import MessageService
from src.services.user_service import UserService


async def get_user_by_token(
    token: Annotated[str | None, Query()] = None,
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    current_user = await UserService.get_current_user(token)

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return current_user


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        del self.active_connections[username]

    async def send_personal_message(self, message: SendMessage):
        sender = message.sender_username
        receiver = message.receiver_username
        text = message.text
        formatted_message = f"[{datetime.utcnow().strftime('%d/%m/%y %H:%M')}] {sender} для {receiver}: {text}"

        if receiver in self.active_connections:
            await self.send_message_to_user(
                receiver,
                SendMessage(
                    sender_username=sender,
                    receiver_username=receiver,
                    text=formatted_message,
                ),
            )
        else:
            await self.send_message_to_user(
                sender,
                SendMessage(
                    sender_username=sender,
                    receiver_username=receiver,
                    text=f"Пользователь '{receiver}' сейчас не в сети, он увидит Ваше сообщение когда зайдет в чат.",
                ),
            )

        if sender != receiver:
            await MessageService.create_message(sender, receiver, text)

    async def show_chat_message(self, message: SendMessage):
        sender = message.sender_username
        text = message.text
        receiver = message.receiver_username
        formatted_message = f"[{datetime.utcnow().strftime('%d/%m/%y %H:%M')}] {sender} для {receiver}: {text}"
        await self.send_message_to_user(
            sender,
            SendMessage(
                sender_username=sender,
                receiver_username=receiver,
                text=formatted_message,
            ),
        )

    async def send_message_to_user(self, username: str, message: SendMessage):
        if username in self.active_connections:
            websocket = self.active_connections[username]
            await websocket.send_text(message.text)

    async def broadcast(self, message: str):
        for websocket in self.active_connections.values():
            await websocket.send_text(message)


manager = ConnectionManager()
