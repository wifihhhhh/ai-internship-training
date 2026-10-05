from src.database import Base, engine
from src.models import Task

Base.metadata.create_all(bind=engine)
print("SQLite tables created.")