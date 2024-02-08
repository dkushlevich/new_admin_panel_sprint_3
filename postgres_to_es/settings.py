from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str 
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str 
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    REDIS_PORT: str
    REDIS_HOST: str
    REDIS_PASSWORD: str

    ELASTIC_HOST: str
    ELASTIC_PORT: str

    TABLE_NAMES: list
    BATCH_SIZE: int
    LOOP_SLEEP_TIME: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
