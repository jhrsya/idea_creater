"""
Vercel 部署优化配置文件
"""
import os
import tempfile
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class VercelSettings(BaseSettings):
    """Vercel 部署设置"""
    
    # 项目基础设置
    PROJECT_NAME: str = "Idea Creator"
    VERSION: str = "1.0.0"
    DEBUG: bool = False  # 生产环境关闭调试
    
    # 路径设置 - 使用临时目录
    BASE_DIR: Path = Path(tempfile.gettempdir()) / "idea_creator"
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # 数据库设置 - 使用内存数据库
    DATABASE_URL: str = "sqlite:///:memory:"
    
    # ArXiv API设置
    ARXIV_MAX_RESULTS: int = 50  # 减少数量避免超时
    ARXIV_SORT_BY: str = "submittedDate"
    ARXIV_SORT_ORDER: str = "descending"
    
    # DeepSeek API设置
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 3000  # 减少token数量
    DEEPSEEK_TEMPERATURE: float = 0.7
    
    # 文件处理设置 - 限制大小
    MAX_PDF_SIZE_MB: int = 10  # 减少大小限制
    SUPPORTED_LANGUAGES: list = ["en", "zh"]
    
    # 爬取设置 - 优化性能
    CRAWL_DELAY: float = 0.5  # 减少延迟
    MAX_RETRIES: int = 2  # 减少重试次数
    TIMEOUT: int = 15  # 减少超时时间
    
    # 日志设置
    LOG_LEVEL: str = "WARNING"  # 减少日志输出
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    
    # Web UI设置
    STREAMLIT_PORT: int = 8501
    STREAMLIT_HOST: str = "0.0.0.0"
    
    # Vercel 特定设置
    VERCEL_ENV: str = os.getenv("VERCEL_ENV", "development")
    VERCEL_URL: str = os.getenv("VERCEL_URL", "localhost")
    
    # 性能优化设置
    MAX_CONCURRENT_REQUESTS: int = 2
    REQUEST_TIMEOUT: int = 300  # 5分钟超时
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = VercelSettings()

# 确保必要的目录存在（在临时目录中）
def create_temp_directories():
    """创建临时目录"""
    try:
        directories = [
            settings.DATA_DIR,
            settings.LOGS_DIR,
            settings.DATA_DIR / "papers",
            settings.DATA_DIR / "extracted",
            settings.DATA_DIR / "results"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        # 在无服务器环境中可能无法创建目录，忽略错误
        pass

# 获取临时文件路径
def get_temp_file_path(filename: str) -> Path:
    """获取临时文件路径"""
    return Path(tempfile.gettempdir()) / filename

# 清理临时文件
def cleanup_temp_files():
    """清理临时文件"""
    try:
        import shutil
        if settings.DATA_DIR.exists():
            shutil.rmtree(settings.DATA_DIR)
    except Exception:
        pass

# 初始化时创建临时目录
create_temp_directories() 