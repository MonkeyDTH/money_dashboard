from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_path: str = str(Path(__file__).parent.parent / "data" / "money.db")
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
