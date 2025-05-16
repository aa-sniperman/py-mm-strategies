from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Get the project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parents[0]
dotenv_path = PROJECT_ROOT / ".env"

class TelegramConfig(BaseSettings):
    bot_token: str = Field(..., validation_alias="BOT_TOKEN")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")

class ExecutorConfig(BaseSettings):
    endpoint: str = Field(..., validation_alias="EXECUTOR_ENDPOINT")
    username: str = Field(..., validation_alias="EXECUTOR_USERNAME")
    api_secret: str = Field(..., validation_alias="EXECUTOR_SECRET")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")

class RedisConfig(BaseSettings):
    dl_host: str = Field(default="localhost", validation_alias="DL_REDIS_HOST")
    dl_password: str = Field(..., validation_alias="DL_REDIS_PASSWORD")
    dl_db: int = Field(..., validation_alias="DL_REDIS_DB")
    dl_username: str = Field(..., validation_alias="DL_REDIS_USERNAME")
    
    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")

class KeysConfig(BaseSettings):
    the20s_endpoint: str = Field(..., validation_alias="THE20S_ENDPOINT")
    the20s_key: str = Field(..., validation_alias="THE20S_KEY")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")

class Settings(BaseSettings):
    redis: RedisConfig = RedisConfig()
    keys: KeysConfig = KeysConfig()
    executor: ExecutorConfig = ExecutorConfig()
    telegram: TelegramConfig = TelegramConfig()

# Instantiate settings
settings = Settings()