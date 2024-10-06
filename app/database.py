import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Определяем базу данных в зависимости от переменной окружения TESTING
if os.getenv("TESTING"):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Тестовая БД (SQLite)
else:
    SQLALCHEMY_DATABASE_URL = "postgresql://user:password1@db:5432/wallet_db"  # Продакшн БД (PostgreSQL)

# Создаем движок базы данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()