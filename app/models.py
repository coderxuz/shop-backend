from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from app.database import Base, engine


class Images(Base):
    __tablename__ = "images"
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
    role = Column(Enum("customer", "seller", name="role_enum"), nullable=False)
    user_img = Column(Integer, ForeignKey("images.id"))

    order = relationship("Order", back_populates="customer")
    basket = relationship("Basket", back_populates="customer")


class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(String, nullable=False)
    description = Column(String, nullable=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(Date, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    prod_img = Column(Integer, ForeignKey("images.id"), nullable=False)


class Basket(Base):
    __tablename__ = "basket"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    customer = relationship("User", back_populates="basket")


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum("pending", "delivered", name="status_enum", nullable=False))
    total_amount = Column(Float)
    customer = relationship("User", back_populates="order")

    def total_amount(self, session):
        total = 0.0
        baskets = (
            session.query(Basket).filter(Basket.customer_id == self.customer_id).all()
        )
        for basket in baskets:
            product = (
                session.query(Products).filter(Products.id == basket.product_id).first()
            )
            if product:
                total += product.price * basket.quantity
        self.total_amount = total
        return self.total_amount


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
