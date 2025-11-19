from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 7777
    APP_DEBUG: bool = True
    SERVER_TITLE: str = "AI horoscope API"
    SERVER_DESCRIPTION: str = "API for cislenka.cz application"
    SERVER_VERSION: str = "0.1.1"
    LOG_LEVEL: str = "DEBUG"
    PROJECTS_DIR: str = "project_data"
    CORS_ALLOW_ORIGINS: list[str] = Field(
        default=["*"],
        description="List of allowed origins for CORS.",
    )
    MONGO_DB_NAME: str = "db"
    MONGO_DB_URL: str = "mongodb://localhost:27017"

    GEMINI_API_URL: str = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
    )
    GEMINI_API_KEY: str = "your_api_key_here"
    REQUEST_RETRY_COUNT: int = 5

    GOTENBERG_API_URL: str = "http://localhost:5001/forms/chromium/convert/html"
    GOTENBERG_AUTH_USERNAME: str = "gotenberg"
    GOTENBERG_AUTH_PASSWORD: str = "gotenberg"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class DBCollectionNamesSetting(BaseSettings):
    ACCESS_CODES: str = "access_codes"
    HOROSCOPES: str = "horoscopes"
    HOROSCOPES_PDF: str = "horoscopes_pdf"


DB_NAMES = DBCollectionNamesSetting()
SERVER_SETTINGS = Settings()
