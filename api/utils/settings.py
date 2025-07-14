import os
from pydantic_settings import BaseSettings
from decouple import config
from pathlib import Path


# Use this to build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """ Class to hold application's config values."""

    PYTHON_ENV: str = config("PYTHON_ENV")
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_EXPIRY: int = config("JWT_REFRESH_EXPIRY")

    APP_URL: str = config("APP_URL")
    JOB_APP_URL: str = config("JOB_APP_URL")

    MAIL_USERNAME: str = config("MAIL_USERNAME")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD")
    MAIL_FROM: str = config("MAIL_FROM")
    MAIL_PORT: int = config("MAIL_PORT")
    MAIL_SERVER: str = config("MAIL_SERVER")

    # Database configurations
    DB_HOST: str = config("DB_HOST")
    DB_PORT: int = config("DB_PORT", cast=int)
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_NAME: str = config("DB_NAME")
    DB_TYPE: str = config("DB_TYPE")
    DB_URL: str = config("DB_URL")

    FLUTTERWAVE_SECRET: str = config("FLUTTERWAVE_SECRET")
    FLW_SECRET_HASH: str = config("FLW_SECRET_HASH")
    STRIPE_SECRET: str = config("STRIPE_SECRET")

    OPENAI_API_KEY: str = config("OPENAI_API_KEY")
    ASSEMBLYAI_API_KEY: str = config("ASSEMBLYAI_API_KEY")
    OPENROUTER_API_KEY: str = config("OPENROUTER_API_KEY")
    GOOEY_API_KEY: str = config("GOOEY_API_KEY")
    DEEPGRAM_API_KEY: str = config("DEEPGRAM_API_KEY")
    UNREAL_SPEECH_API_KEY: str = config("UNREAL_SPEECH_API_KEY")
    REPLICATE_API_TOKEN: str = config("REPLICATE_API_TOKEN")
    
    PIXABAY_API_KEY: str = config("PIXABAY_API_KEY")
    # FREEPIK_API_KEY: str = config("FREEPIK_API_KEY")
    UNSPLASH_ACCESS_KEY: str = config("UNSPLASH_ACCESS_KEY")
    UNSPLASH_SECRET_KEY: str = config("UNSPLASH_SECRET_KEY")
    PEXELS_API_KEY: str = config("PEXELS_API_KEY")

    MINIO_ACCESS_KEY: str = config("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = config("MINIO_SECRET_KEY")
    
    YOUTUBE_USERNAME: str = config("YOUTUBE_USERNAME")
    YOUTUBE_PASSWORD: str = config("YOUTUBE_PASSWORD")
    
    TWITTER_BEARER_TOKEN: str = config("TWITTER_BEARER_TOKEN")

    TEMP_DIR: str = os.path.join(Path(__file__).resolve().parent.parent.parent, 'tmp', 'media')
    FRONTEND_MAGICLINK_URL : str = config("FRONTEND_MAGICLINK_URL")
    
    @property
    def ACTIVATE_TOOL_TRACKING(self) -> bool:
        # Get the environment variable as a string
        activate_tool_tracking_str = config("ACTIVATE_TOOL_TRACKING", default="True")
        # Convert the string to a boolean, defaulting to True if conversion fails
        return activate_tool_tracking_str.lower() in {"true", "1", "yes"}  


settings = Settings()
