from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DB_URL = "postgresql+psycopg2://postgres:coderxuz@localhost/learn"

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db  # Sessiya yaratish
    finally:
        db.close()  # Sessiyani yopish
