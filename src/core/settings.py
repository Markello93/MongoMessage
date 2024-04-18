from functools import cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    DEBUG: bool = False
    APP_ROOT_PATH: str = ""
    SECRET_KEY: str = "2178281836b65150405c82bfc132b59dbd854e91b79492909647e26adbf5a958"
    ALGORITHM: str = "HS256"
    TOKEN_LIFETIME: int = 15
    REFRESH_TOKEN_LIFETIME: int = 10080
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str = "mongo_message"
    MONGO_USER: str = ""
    MONGO_PASS: str = ""

    @property
    def mongo_url(self) -> str:
        """Генерация ссылки для подключения к MongoDB."""
        if self.MONGO_USER and self.MONGO_PASS:
            return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"
        else:
            return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"

    class Config:
        env_file = ".env"


@cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
