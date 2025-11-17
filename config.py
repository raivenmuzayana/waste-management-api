from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    # Format: "mysql+mysqlconnector://USER:PASSWORD@HOST:PORT/DB_NAME"
    DATABASE_URL: str = "mysql+mysqlconnector://root:password@localhost:3306/waste_db"
    
    # JWT
    JWT_SECRET_KEY: str = "super-secret-key-anda-harus-diganti"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1 hari

    class Config:
        env_file = ".env"  # Muat variabel dari file .env

settings = Settings()