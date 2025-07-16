from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    youtube_api_key: str
    webhook_secret: str

    youtube_api_url: str = "https://www.googleapis.com/youtube/v3/search"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
