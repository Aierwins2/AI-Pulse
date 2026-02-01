"""应用配置"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    dashscope_api_key: str = "YOUR_DASHSCOPE_API_KEY"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/aipulse.db"

    # Data retention
    data_retention_days: int = 7

    # Scheduler
    crawler_schedule_hour: int = 9  # 每天北京时间 9:00 执行
    crawler_schedule_minute: int = 0

    # AI Model
    ai_model: str = "qwen-plus"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
