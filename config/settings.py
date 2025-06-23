"""
项目配置文件
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""
    
    # 项目基础设置
    PROJECT_NAME: str = "Idea Creator"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 路径设置
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # 数据库设置
    DATABASE_URL: str = "sqlite:///./data/idea_creator.db"
    
    # ArXiv API设置
    ARXIV_MAX_RESULTS: int = 100
    ARXIV_SORT_BY: str = "submittedDate"
    ARXIV_SORT_ORDER: str = "descending"
    
    # AI模型设置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.7
    
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # 文件处理设置
    MAX_PDF_SIZE_MB: int = 50
    SUPPORTED_LANGUAGES: list = ["en", "zh"]
    
    # 爬取设置
    CRAWL_DELAY: float = 1.0  # 请求间隔（秒）
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # 日志设置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    
    # Web UI设置
    STREAMLIT_PORT: int = 8501
    STREAMLIT_HOST: str = "localhost"
    
    # DeepSeek API设置
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # AI_PROVIDER设置
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()

# 确保必要的目录存在
def create_directories():
    """创建必要的目录"""
    directories = [
        settings.DATA_DIR,
        settings.LOGS_DIR,
        settings.DATA_DIR / "papers",
        settings.DATA_DIR / "extracted",
        settings.DATA_DIR / "results"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# 初始化时创建目录
create_directories() 