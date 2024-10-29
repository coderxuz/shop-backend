from fastapi import (
    APIRouter,
    HTTPException,
    Header,
    Response,
    Request,
    status,
    Depends,
    UploadFile,
    File,
    Form,
)
import os
from datetime import timedelta, datetime
from app.schemas import UserBase, Created, Login, Token, Login1
from app.database import get_db
from app.models import User
import hashlib
from datetime import timedelta
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import JWTError,jwt
from sqlalchemy.orm import Session
router = APIRouter(prefix="/auth", tags=['AUTH'])

SECRET_KEY = "fe89708897e427a05eb58670e36d9fbfc7da76266081cc62c0064f347dd1e5c7"

ACCESS_TOKEN_EXPIRES_MINUTES = 30
REFRESH_TOKEN_EXPIRES_DAYS = 7
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/form")


def access_token_create(email: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def refresh_token_create(email: str):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS)
    to_encode = {"sub": email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_tokens(email: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = jwt.encode(
        {"sub": email, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    refresh_token = jwt.encode(
        {"sub": email}, SECRET_KEY, algorithm=ALGORITHM
    )  # Refresh token uchun davomiylikni qo'shishingiz mumkin
    return {"access_token": access_token, "refresh_token": refresh_token}


def hash_password(password: str) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(password.encode("utf-8"))
    return md5_hash.hexdigest()


def verify_password(stored_hash: str, password_to_check: str) -> bool:
    return stored_hash == hash_password(password_to_check)


@router.post(
    "/sign-up",
    response_model=Created,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "User already exists",
            "content": {
                "application/json": {"example": {"detail": "User already exists"}}
            },
        }
    },
)
async def create_user(user: UserBase, db:Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        email=user.email,
        role=user.role,
        hashed_password=hash_password(user.password),
        user_img=None,
    )
    db.add(db_user)
    tokens = create_tokens(email=user.email)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    db.commit()
    return {
        "message": "user successfully created",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post(
    "/login",
    response_model=Created,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "User not found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        }
    },
)
async def login_user(user: Login, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(db_user.hashed_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password incorrect",
        )
    tokens = create_tokens(email=user.email)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    return {
        "message": "success logined",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def get_token_from_header(request: Request):
    authorization: str = request.headers.get("Authorization")
    if authorization is None:
        raise HTTPException(status_code=401, detail="Token doesn't exist")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer' format is wrong")

    return token


def verify_token(request: Request):
    token = get_token_from_header(request)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Noto'g'ri yoki tugagan token")


@router.get(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    dependencies=[Depends(oauth2_scheme)],
)
async def refreshing(request: Request):
    payload = verify_token(request)
    if payload:
        print(payload)
        tokens = create_tokens(payload["sub"])
        access_token = tokens["access_token"]
        return {
        "access_token": access_token,
        "token_type":'bearer'
    }


@router.post(
    "/form",
    response_model=Created,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Foydalanuvchi topilmadi",
            "content": {
                "application/json": {"example": {"detail": "Foydalanuvchi topilmadi"}}
            },
        }
    },
)
async def login_user(
    user: Annotated[OAuth2PasswordRequestForm, Depends()], db:Session = Depends(get_db)
):
    try:
        db_user = db.query(User).filter(User.email == user.username).first()
        if not db_user or not verify_password(db_user.hashed_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email yoki parol noto'g'ri",
            )
        tokens = create_tokens(email=user.username)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        return {
            "message": "Muvaffaqiyatli kirish",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.close()


@router.get("/protected-endpoint")
async def protected_endpoint(token: str = Depends(oauth2_scheme)):
    return {"message": "Bu himoyalangan endpoint"}
