from sqlalchemy import Column, Integer, String, Enum, ForeignKey,Date
from app.database import Base, engine

class Images(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_path = Column(String, nullable=False) 
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    gender = Column(Enum("male", "female", name="gender_enum"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum('customer','seller',name = 'role_enum'), nullable=False)
    user_img = Column(Integer, ForeignKey('images.id'))
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "email": self.email,
            "role":self.role,
            "profile_photo": self.image_path,
        }

class Products(Base):
    __tablename__='products'
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(String,nullable=False)
    description = Column(String,nullable=True)
    seller_id = Column(Integer,ForeignKey('users.id'), nullable=False)
    created_at = Column(Date,nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    prod_img = Column(Integer, ForeignKey('images.id'),nullable=False)

def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
