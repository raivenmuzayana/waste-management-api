from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Config
    JWT_SECRET_KEY: str = "rahasia_banget_jangan_disebar"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 

    class Config:
        env_file = ".env"
        extra = "ignore"  # <--- TAMBAHAN PENTING! (Agar tidak error baca DB_HOST dkk)

settings = Settings()