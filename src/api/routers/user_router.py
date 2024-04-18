from fastapi import APIRouter, Depends, File, UploadFile

from src.api.schemas.user_schema import (UserAuth, UserCreate, UserFind,
                                         UserOut, UserUpdateRequest)
from src.models.user_models import User
from src.services.user_service import UserService

user_router = APIRouter()


@user_router.post("/create", summary="Создание пользователя", response_model=UserCreate)
async def create_user(schema: UserAuth):
    return await UserService.create_user(schema)


@user_router.get(
    "/me", summary="Информация об авторизированном пользователе", response_model=UserOut
)
async def get_me(user: User = Depends(UserService.get_current_user)):
    return user


@user_router.post(
    "/update", summary="Изменение данных пользователя", response_model=UserOut
)
async def update_user(
    schema: UserUpdateRequest, user: User = Depends(UserService.get_current_user)
):
    return await UserService.update_user(user.user_id, schema)


@user_router.get(
    "/{username}/", summary="Поиск пользователя по username", response_model=UserFind
)
async def get_user_by_username(username: str):
    user = await UserService.get_user_by_username(username)

    return user


@user_router.post(
    "/add_picture", summary="Загрузить изображение и привязать его к пользователю"
)
async def add_picture(
    file: UploadFile = File(...),
    user: User = Depends(UserService.get_current_user),
):
    picture_path = await UserService.save_picture(user.username, file)
    await UserService.update_user_picture(user.user_id, picture_path)
    return {"message": "Изображение успешно добавлено к пользователю"}
