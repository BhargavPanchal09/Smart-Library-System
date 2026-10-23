from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    FIREBASE_CREDENTIALS: str = "service-account.json"
    FIREBASE_JSON: str | None = None
    CORS_ORIGINS: str = "http://localhost:3000"
    ENABLE_DEMO_ENDPOINTS: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
