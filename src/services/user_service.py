from datetime import datetime
from typing import Optional
from uuid import UUID

import pymongo
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from src.core.secure import get_password, verify_password
from src.core.settings import settings
from src.models.user_models import User
from src.api.schemas.auth_schema import TokenPayload
from src.api.schemas.user_schema import UserAuth, UserUpdateRequest

reuseable_oauth = OAuth2PasswordBearer(tokenUrl=f"auth/login", scheme_name="JWT")


class UserService:

    @staticmethod
    async def create_user(schema: UserAuth) -> User:
        user_exists = await User.find_one(
            {"$or": [{"username": schema.username}, {"email": schema.email}]}
        )
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists",
            )

        user = User(
            username=schema.username,
            email=schema.email,
            hashed_password=get_password(schema.password),
        )
        await user.save()
        return user

    @staticmethod
    async def authenticate(username: str, password: str) -> Optional[User]:
        user = await UserService.get_user_by_username(username=username)
        if not user:
            return None
        if not verify_password(password=password, hashed_pass=user.hashed_password):
            return None

        return user

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        user = await User.find_one(User.username == username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{username}' not found")
        return user

    @staticmethod
    async def get_user_by_id(id: UUID) -> Optional[User]:
        user = await User.find_one(User.user_id == id)
        return user

    @staticmethod
    async def update_user(id: UUID, schema: UserUpdateRequest) -> User:
        user = await User.find_one(User.user_id == id)
        if not user:
            raise pymongo.errors.OperationFailure("User not found")

        await user.update({"$set": schema.dict(exclude_unset=True)})
        return user

    @staticmethod
    async def get_current_user(token: str = Depends(reuseable_oauth)) -> User:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = TokenPayload(**payload)

            if datetime.fromtimestamp(token_data.exp) < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await UserService.get_user_by_id(token_data.sub)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find user",
            )

        return user
