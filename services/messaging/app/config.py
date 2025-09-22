from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings():
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    WEBHOOK_SECRET_TOKEN: str | None = os.getenv("WEBHOOK_SECRET_TOKEN")
    USER_SERVICE_BASE: str = os.getenv("USER_SERVICE_BASE")
    AGENT_SERVICE_BASE: str | None = os.getenv("AGENT_SERVICE_BASE")
    REQUEST_TIMEOUT: int = 60
    LOG_LEVEL: str = "INFO"

settings = Settings()
