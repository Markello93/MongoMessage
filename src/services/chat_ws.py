from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
    Query,
)
from fastapi.responses import HTMLResponse
from typing import Annotated

from starlette.exceptions import HTTPException

from src.api.schemas.message_schema import SendMessage
from src.models.user_models import User
from src.services.message_service import MessageService
from src.services.user_service import UserService

chat_router = APIRouter()


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

        if receiver in self.active_connections:
            await self.send_message_to_user(
                receiver,
                SendMessage(
                    sender_username=sender,
                    receiver_username=receiver,
                    text=f"{sender} для {receiver}: {text}",
                ),
            )
        else:
            await self.send_message_to_user(
                sender,
                SendMessage(
                    sender_username=sender,
                    receiver_username=receiver,
                    text=f"User '{receiver}' сейчас не в сети, он увидит Ваше сообщение, когда зайдет в чат.",
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

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
</head>
<body>
    <h1>WebSocket Chat</h1>
    <form action="" onsubmit="connectWebSocket(event)">
        <label>Token: <input type="text" id="tokenInput" autocomplete="off" /></label>
        <button type="submit">Connect</button>
    </form>
    <ul id="messages"></ul>
    <input type="text" id="messageInput" autocomplete="off" />
    <button onclick="sendMessage()">Send</button>

    <script>
        let ws;

        async function connectWebSocket(event) {
            event.preventDefault();
            const token = document.getElementById("tokenInput").value;
            try {
                ws = new WebSocket(`ws://localhost:8000/ws/?token=${token}`);
                ws.onmessage = function(event) {
                    const messages = document.getElementById("messages");
                    const message = document.createElement("li");
                    message.textContent = event.data;
                    messages.appendChild(message);
                };
            } catch (error) {
                console.error("Failed to connect:", error);
            }
        }

        function sendMessage() {
            const messageInput = document.getElementById("messageInput");
            const message = messageInput.value;
            ws.send(message);
            messageInput.value = "";
        }
    </script>
</body>
</html>

"""


@chat_router.get("/")
async def get():
    return HTMLResponse(html)


@chat_router.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket, user: User = Depends(get_user_by_token)
):
    await manager.connect(websocket, user.username)
    last_messages = await MessageService.get_last_messages_for_user(user.username)
    for message in last_messages:
        formatted_time = message.created_at.strftime("%d/%m/%y %H:%M")
        formatted_message = f"[{formatted_time}] {message.sender_username} для {message.receiver_username}: {message.text}"
        # formatted_message = f"{message.sender_username} для {message.receiver_username}: {message.text}"
        await websocket.send_text(formatted_message)

    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("/pm"):
                _, receiver, message_text = data.split(" ", 2)
                if receiver == user.username:
                    await websocket.send_text(
                        "You cannot send a private message to yourself."
                    )
                else:
                    await manager.send_personal_message(
                        SendMessage(
                            sender_username=user.username,
                            receiver_username=receiver,
                            text=message_text,
                        )
                    )
                    await manager.show_chat_message(
                        SendMessage(
                            sender_username=user.username,
                            receiver_username=receiver,
                            text=message_text,
                        )
                    )
            else:
                formatted_time = datetime.utcnow().strftime("%d/%m/%y %H:%M")
                formatted_message = f"[{formatted_time}] {user.username}: {data}"
                await manager.broadcast(formatted_message)
    except WebSocketDisconnect:
        manager.disconnect(user.username)
