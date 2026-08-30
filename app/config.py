from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PSQL_DB_")

    database: str
    username: str
    password: str
    host: str
    port: str


postgres_settings = PostgresSettings()

DATABASE_URL = "postgres://{}:{}@{}:{}/{}".format(
    postgres_settings.username,
    postgres_settings.password,
    postgres_settings.host,
    postgres_settings.port,
    postgres_settings.database,
)


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str
    port: int
    db: int
    token_expiration_time: int


redis_settings = RedisSettings()


class MinioSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MINIO_")

    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    secure: bool


minio_settings = MinioSettings()

models = ["app.authentication.models", "aerich.models"]
