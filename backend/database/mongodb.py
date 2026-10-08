from pymongo import MongoClient
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str
    mongodb_database: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()

client = MongoClient(settings.mongodb_uri)

db = client[settings.mongodb_database]


def get_database():
    return db


def test_connection():
    client.admin.command("ping")
    print("MongoDB connection successful!")