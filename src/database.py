from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import settings

connect_args = (
    {"check_same_thread": False} 
    if settings.database_url.startswith("sqlite") 
    else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args,)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False,  # 禁用过期行为，避免在提交后访问已删除的对象
)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()