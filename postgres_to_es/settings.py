from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str 
    postgres_password: str
    postgres_db: str 
    postgres_host: str
    postgres_port: str

    redis_port: str
    redis_host: str
    redis_password: str

    elastic_host: str
    elastic_port: str
    elastic_index: str

    table_names: list
    batch_size: int
    loop_sleep_time: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
