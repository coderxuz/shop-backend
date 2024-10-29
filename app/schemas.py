from pydantic import BaseModel, EmailStr
from enum import Enum
from fastapi import UploadFile,File,Form
from typing import Optional, Union

class Gender(str, Enum):
    male = 'male'
    female = 'female'

class Value(str, Enum):
    name = 'name'
    price = 'price'
    date_new = 'date-new'
    date_old = 'date-old'
    stock_quantity = 'stock_quantity'
class Role(str, Enum):
    seller = 'seller'
    customer = 'customer'

class UserBase(BaseModel):
    first_name: str 
    last_name: str
    gender: Gender
    email: EmailStr
    password:str
    role:Role
    class Config:
        orm_mode = True
class UserResponse(BaseModel):
    id:str
    first_name: str
    last_name: str
    gender: Gender
    email: EmailStr
    profile_photo: str= None
    role:Role
class Created(BaseModel):
    message:str
    access_token:str
    refresh_token:str
class Login(BaseModel):
    email:str
    password:str
class Token(BaseModel):
    access_token:str
    token_type:str='bearer'
class Upload(BaseModel):
    message:str='uploaded'
class Prods(BaseModel):
    id:int
    img:str
    name:str
    price:str
class ProdsSeller(BaseModel):
    products:list[Prods]
    seller_id:Optional[int]
class Login1(BaseModel):
    username:str
    password:str
class Uploaded_id(BaseModel):
    image_id:int
class ProdCreated(BaseModel):
    message:str='created'
class ProdForm(BaseModel):
    name:str
    price:Union[float,int]
    description:str
    stock_quantity:int
    prod_img:int
class ProdMain(BaseModel):
    name:str
    price:Union[float,int]
    description:str
    stock_quantity:int
    prod_img:str
    seller_id :Optional[int]
class ProdChange(BaseModel):
    image_id:Optional[int]
    product_id:int
    name:str
    price:Union[float,int]
    description:str
    stock_quantity:int
class Changed(BaseModel):
    message:str
class BasketData(BaseModel):
    product_id:int
    quantity:int
    