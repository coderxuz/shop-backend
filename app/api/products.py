from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Request,
    Query,
)
from datetime import timedelta, datetime
from app.database import get_db
from app.models import User, Products, Images
from datetime import timedelta
from pydantic import BaseModel
from app.schemas import (
    ProdsSeller,
    ProdCreated,
    ProdForm,
    Value,
    ProdMain,
    ProdChange,
    Changed,
)
from app.api.login_register import oauth2_scheme, verify_token
from typing import Optional
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

router = APIRouter(prefix="/prods", tags=["PRODS"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ProdsSeller,
    dependencies=[Depends(oauth2_scheme)],
)
async def prods(request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    current_user = payload["sub"]
    global db_user
    db_user = db.query(User).filter(User.email == current_user).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user not found"
        )

    if db_user and db_user.role == "seller":
        prods = db.query(Products).filter(Products.seller_id == db_user.id).all()
        prods_list = []
        for item in prods:
            image = db.query(Images).filter(Images.id == item.prod_img).first()
            image_url = f"{request.url.scheme}://{request.url.netloc}/images/{image.id}"
            prods_list.append(
                {
                    "id": item.id,
                    "img": image_url,
                    "name": item.name,
                    "price": item.price,
                }
            )
        result = {"products": prods_list, "seller_id": db_user.id}
        return result
    prods = db.query(Products).all()
    prods_list = []
    for item in prods:
        image = db.query(Images).filter(Images.id == item.prod_img).first()
        image_url = f"{request.url.scheme}://{request.url.netloc}/images/{image.id}"
        prods_list.append(
            {"id": item.id, "img": image_url, "name": item.name, "price": item.price}
        )
        result = {"products": prods_list, "seller_id": None}
    return result


@router.post("/add", response_model=ProdCreated, dependencies=[Depends(oauth2_scheme)])
async def add_prod(form: ProdForm, request: Request, db: Session = Depends(get_db)):
    try:
        payload = verify_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token expired or invalid {e}",
        )
    user_email = payload["sub"]
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user.role == "seller":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not seller"
        )
    now = datetime.utcnow()
    user_id = db_user.id
    new_prod = Products(
        name=form.name,
        price=form.price,
        description=form.description,
        seller_id=user_id,
        created_at=now,
        stock_quantity=form.stock_quantity,
        prod_img=form.prod_img,
    )
    db.add(new_prod)
    db.commit()
    db.close()
    return {"message": "created"}


@router.get(
    "/sort",
    status_code=status.HTTP_200_OK,
    response_model=ProdsSeller,
    dependencies=[Depends(oauth2_scheme)],
)
async def sorting(
    request: Request,
    db: Session = Depends(get_db),
    sort: Optional[Value] = Query(None, description='sort value for example "name"'),
    value: str = Query(..., description="Value for search"),
):
    payload = verify_token(request)
    current_user = payload["sub"]
    db_user = db.query(User).filter(User.email == current_user).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user not found"
        )
    global prods
    if db_user.role == "seller":
        prods = db.query(Products).filter(
            Products.seller_id == db_user.id, Products.name.ilike(f"%{value}%")
        )
    else:
        prods = db.query(Products).filter(Products.name.ilike(f"%{value}%"))
    if sort == Value.name:
        prods = prods.order_by(asc(Products.name))
    if sort == Value.date_new:
        prods = prods.order_by(asc(Products.created_at))
    if sort == Value.date_old:
        prods = prods.order_by(desc(Products.created_at))
    if sort == Value.price:
        prods = prods.order_by(asc(Products.price))
    if sort == Value.stock_quantity:
        prods = prods.order_by(asc(Products.stock_quantity))
    prods_list = []
    for item in prods:
        image = db.query(Images).filter(Images.id == item.prod_img).first()
        image_url = f"{request.url.scheme}://{request.url.netloc}/images/{image.id}"
        prods_list.append(
            {"id": item.id, "img": image_url, "name": item.name, "price": item.price}
        )
    result = {"products": prods_list, "seller_id": db_user.id}
    db.close()
    return result


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ProdMain,
    dependencies=[Depends(oauth2_scheme)],
)
async def prodMain(request: Request, id: int, db: Session = Depends(get_db)):
    payload = verify_token(request)
    current_user = payload["sub"]
    global db_user
    db_user = db.query(User).filter(User.email == current_user).first()
    prod = db.query(Products).filter(Products.id == id).first()
    if db_user and prod and db_user.role == "seller" and prod.seller_id == db_user.id:
        return {
            "id": prod.id,
            "name": prod.name,
            "price": prod.price,
            "description": prod.description,
            "stock_quantity": prod.stock_quantity,
            "prod_img": f"{request.url.scheme}://{request.url.netloc}/images/{prod.prod_img}",
            "seller_id": db_user.id,
        }
    return {
        "id": prod.id,
        "name": prod.name,
        "price": prod.price,
        "description": prod.description,
        "stock_quantity": prod.stock_quantity,
        "prod_img": f"{request.url.scheme}://{request.url.netloc}/images/{prod.prod_img}",
        "seller_id": None,
    }


@router.put("/change", response_model=Changed, dependencies=[Depends(oauth2_scheme)])
async def update_prod(
    data: ProdChange, request: Request, db: Session = Depends(get_db)
):
    payload = verify_token(request)
    current_user = payload["sub"]
    db_user = db.query(User).filter(User.email == current_user).first()
    if not current_user or not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user not found"
        )
    prod = db.query(Products).filter(Products.id == data.product_id).first()
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user not found"
        )
    if db_user.id != prod.seller_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="product isn't user's"
        )
    if data.image_id:
        prod.prod_img = data.image_id
    prod.name = data.name
    prod.price = data.price
    prod.stock_quantity = data.stock_quantity
    prod.description = data.description
    db.commit()
    db.refresh(prod)
    return {"message": "changed"}
