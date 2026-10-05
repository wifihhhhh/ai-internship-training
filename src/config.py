# 从环境变量读取配置

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件中的环境变量

def parse_bool(value: str) -> bool:
    """将字符串解析为布尔值"""
    return value.lower() in ("true", "1", "yes", "on")

@dataclass
class Settings:
    """应用程序配置类"""
    app_name: str
    debug: bool
    log_level: str
    database_url: str

def get_settings() -> Settings:
    """从环境变量中获取配置"""
    
    return Settings(
        app_name=os.getenv("APP_NAME", "AI Internship Training"),
        debug=parse_bool(os.getenv("DEBUG", "false")), 
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(), # 读取 LOG_LEVEL；若没配置，就使用默认值 INFO
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/tasks.db")  # 读取 DATABASE_URL；若没配置，就使用默认值 sqlite:///./data/tasks.db
    )

settings = get_settings()