from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings (BaseSettings):
    APP_NAME : str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE : int
    MONGODB_DATABASE :str
    MONGODB_URL: str

    class config:
        env_file = '.env'

def get_setings ():
    return Settings()
