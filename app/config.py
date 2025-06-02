from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "go-bah-team"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
