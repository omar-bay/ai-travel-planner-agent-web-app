from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    DATABASE_URL: str = Field(...)
    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    OPENAI_API_KEY: str | None = None


    class Config:
        env_file = ".env"


settings = Settings()


if settings.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY