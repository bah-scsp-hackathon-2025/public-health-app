from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "go-bah-team"
    access_token_expire_minutes: int = 60
    
    # FastAPI Server Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8001

    class Config:
        env_file = ".env"


settings = Settings()
