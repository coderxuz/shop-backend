from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DB_URL = "postgresql+psycopg2://postgres:coderxuz@localhost/learn"
DB_URL = 'postgresql://shop_base_user:dkm1IuvkCYj7bSbNE0pt7dnXNHs0lhfE@dpg-csjnv1u8ii6s73d6ccn0-a.oregon-postgres.render.com/shop_base'
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db  # Sessiya yaratish
    finally:
        db.close()  # Sessiyani yopish
