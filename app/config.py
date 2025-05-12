from pydantic import AnyUrl, BaseModel, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TgBot(BaseModel):
    token: str
    admin_id: int


class Scraper(BaseModel):
    connection_timeout: float
    max_pool_size: int
    time_delta: float
    time_delta_after_exception: float
    recursion_limit: int
    max_exception_counter: int


class DatabaseConfig(BaseModel):
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    dialect: str = "postgresql"
    driver: str = "asyncpg"
    username: str
    password: str
    address: str
    port: int
    db_name: str

    @computed_field(return_type=PostgresDsn)
    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn(
            f"{self.dialect}+{self.driver}://"
            f"{self.username}:{self.password}@"
            f"{self.address}:{self.port}"
        )


class Proxy(BaseModel):
    type: str
    username: str
    password: str
    address: str
    port: int

    @computed_field(return_type=AnyUrl)
    @property
    def url(self) -> AnyUrl:
        return AnyUrl(
            f"{self.type}://"
            f"{self.username}:{self.password}@"
            f"{self.address}:{self.port}"
        )


class LoggerConfig(BaseModel):
    """
    Configuration for setting up the Loguru logger.

    Attributes:
        logbook_path (str): - Path to the log file.
        logs_format (str): - Format string for log messages.
        rotation_time (str): - Time for daily log file rotation.
    """

    logbook_path: str = "/app/logs/logbook.log"
    logs_format: str = "{time} | {level} | {module}:{line} | {message}"
    rotation_time: str = "08:00"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="GF__",
    )

    tg_bot: TgBot
    proxy: Proxy
    db: DatabaseConfig
    logger: LoggerConfig = LoggerConfig(
        logbook_path="logs/logbook.log",
        logs_format="{time} | {level} | {module}:{line} | {message}",
        rotation_time="08:00",
    )
    scraper: Scraper = Scraper(
        connection_timeout=5.5,
        max_pool_size=16,
        time_delta=1.0,
        time_delta_after_exception=12,
        recursion_limit=3,
        max_exception_counter=100,
    )


settings = Settings()
