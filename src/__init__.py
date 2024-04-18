from fastapi import FastAPI

from src.api.routers.user_router import user_router
from src.api.routers.auth import auth_router
from src.core.settings import settings
from src.api.routers.messenger_router import chat_router
# from src.services.websocket_logic import chat_router


def create_app() -> FastAPI:
    app = FastAPI(title="API мессенджера с регистрацией пользователей",
    description="APi представляет функционал регистрации, доступ в чат осуществляется по JWT access token.",
    version="1.0", debug=settings.DEBUG, root_path=settings.APP_ROOT_PATH)
    app.include_router(user_router, prefix='/users', tags=["users"])
    app.include_router(auth_router, prefix='/auth', tags=["auth"])
    app.include_router(chat_router)

    return app
