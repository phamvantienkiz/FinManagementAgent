from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    WEBHOOK_SECRET_TOKEN: str | None = None
    USER_SERVICE_BASE: str
    AGENT_SERVICE_BASE: str | None = None
    REQUEST_TIMEOUT: int = 10
    LOG_LEVEL: str = "INFO"

settings = Settings()
