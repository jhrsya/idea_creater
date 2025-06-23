"""
日志系统模块
"""
import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logger():
    """设置日志系统"""
    # 移除默认的日志处理器
    logger.remove()
    
    # 添加控制台日志处理器
    logger.add(
        sys.stdout,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # 添加文件日志处理器
    log_file = settings.LOGS_DIR / "idea_creator.log"
    logger.add(
        log_file,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # 添加错误日志文件
    error_log_file = settings.LOGS_DIR / "errors.log"
    logger.add(
        error_log_file,
        format=settings.LOG_FORMAT,
        level="ERROR",
        rotation="5 MB",
        retention="60 days",
        compression="zip"
    )
    
    return logger


# 初始化日志系统
setup_logger() 