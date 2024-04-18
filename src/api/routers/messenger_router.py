from datetime import datetime

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from src.api.schemas.message_schema import SendMessage
from src.models.user_models import User
from src.services.message_service import MessageService
from src.services.websocket_logic import get_user_by_token, manager

chat_router = APIRouter(
    prefix="/messenger",
    tags=["Chat"],
)

templates = Jinja2Templates(directory="src/templates")


@chat_router.get("/")
async def get(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@chat_router.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket, user: User = Depends(get_user_by_token)
):
    await manager.connect(websocket, user.username)
    last_messages = await MessageService.get_last_messages_for_user(user.username)
    for message in last_messages:
        formatted_time = message.created_at.strftime("%d/%m/%y %H:%M")
        formatted_message = f"[{formatted_time}] {message.sender_username} для {message.receiver_username}: {message.text}"
        await websocket.send_text(formatted_message)

    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("/pm"):
                _, receiver, message_text = data.split(" ", 2)
                if receiver == user.username:
                    await websocket.send_text(
                        "Вы не можете отправлять личные сообщения себе."
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
