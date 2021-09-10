from pydantic import BaseSettings


class Settings(BaseSettings):
    url: str
    database: str
    host: str
    password: str
    port: int = 5432
    user: str

    class Config:
        env_file = '.env'
