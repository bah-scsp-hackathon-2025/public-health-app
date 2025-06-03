from pathlib import Path
from pydantic_settings import BaseSettings

# Load environment variables from dotenv if available
try:
    from dotenv import load_dotenv
    # Try multiple locations for .env file
    env_locations = [
        Path(".env"),  # Current directory
        Path("../.env"),  # Parent directory
        Path("../../.env"),  # Two levels up (for nested structures)
    ]

    for env_path in env_locations:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded environment variables from {env_path}")
            break
    else:
        print("No .env file found in standard locations")

except ImportError:
    print("python-dotenv not installed, loading from system environment only")


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "go-bah-team"
    access_token_expire_minutes: int = 60

    # FastAPI Server Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8001

    # MCP Server Configuration
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8000

    # API Keys - Pydantic will automatically load these from environment
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    delphi_epidata_key: str = ""
    
    # LangSmith Configuration
    langsmith_api_key: str = ""
    langsmith_project: str = "public-health-dashboard"
    langsmith_tracing: bool = True

    class Config:
        env_file = [".env", "../.env", "../../.env"]  # Multiple possible locations
        env_file_encoding = 'utf-8'
        case_sensitive = False  # Allow case-insensitive env var names
        extra = 'ignore'  # Ignore extra fields in .env


# Create settings instance after environment is loaded
settings = Settings()
