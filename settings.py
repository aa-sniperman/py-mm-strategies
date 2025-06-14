from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Get the project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parents[0]
dotenv_path = PROJECT_ROOT / ".env"

class The20sConfig(BaseSettings):
    key: str = Field(..., validation_alias="THE20S_KEY")
    endpoint: str = Field(..., validation_alias="THE20S_ENDPOINT")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")

class ClickhouseConfig(BaseSettings):
    host: str = Field(..., validation_alias="DL_CLICKHOUSE_HOST")
    username: str = Field(..., validation_alias="DL_CLICKHOUSE_USERNAME")
    password: str = Field(..., validation_alias="DL_CLICKHOUSE_PASSWORD")
    database: str = Field(..., validation_alias="DL_CLICKHOUSE_DB")
    port: int = Field(..., validation_alias="DL_CLICKHOUSE_PORT")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")


class ApiConfig(BaseSettings):
    api_key: str = Field(..., validation_alias="API_KEY")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")


class TelegramConfig(BaseSettings):
    bot_token: str = Field(..., validation_alias="BOT_TOKEN")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")


class ExecutorConfig(BaseSettings):
    endpoint: str = Field(..., validation_alias="MM_EXECUTOR_ENDPOINT")
    username: str = Field(..., validation_alias="MM_EXECUTOR_USERNAME")
    api_secret: str = Field(..., validation_alias="MM_EXECUTOR_SECRET")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")


class RedisConfig(BaseSettings):
    dl_host: str = Field(default="localhost", validation_alias="DL_REDIS_HOST")
    dl_port: int = Field(..., validation_alias="DL_REDIS_PORT")
    dl_password: str = Field(..., validation_alias="DL_REDIS_PASSWORD")
    dl_db: int = Field(..., validation_alias="DL_REDIS_DB")
    dl_username: str = Field(..., validation_alias="DL_REDIS_USERNAME")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")


class KeysConfig(BaseSettings):
    the20s_endpoint: str = Field(..., validation_alias="THE20S_ENDPOINT")
    the20s_key: str = Field(..., validation_alias="THE20S_KEY")

    model_config = SettingsConfigDict(env_file=dotenv_path, extra="allow")


class Settings(BaseSettings):
    clickhouse: ClickhouseConfig = Field(default_factory=ClickhouseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    keys: KeysConfig = Field(default_factory=KeysConfig)
    executor: ExecutorConfig = Field(default_factory=ExecutorConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    the20s: The20sConfig = Field(default_factory=The20sConfig)


# Instantiate settings
settings = Settings()
