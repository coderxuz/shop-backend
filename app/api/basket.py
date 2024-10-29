from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.database import get_db
from app.models import User, Products, Images, Basket
from app.api.login_register import oauth2_scheme, verify_token
from sqlalchemy.orm import Session
from app.schemas import Changed, BasketData

router = APIRouter(prefix="/basket", tags=["BASKET"])


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Changed,
    dependencies=[Depends(oauth2_scheme)],
)
async def basket(data: BasketData, request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    current_user = payload["sub"]
    db_user = db.query(User).filter(User.email == current_user).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user not found"
        )
    if db_user and db_user.role == "customer":
        basket = Basket(
            customer_id=db_user.id,
            product_id=data.product_id,
            quantity=data.quantity,
        )
        db.add(basket)
        db.commit()
    if db_user.role == "seller":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user is seller"
        )
    return {"message": "added"}

@router.get("", status_code=status.HTTP_200_OK, dependencies=[Depends(oauth2_scheme)])
async def basket(request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    current_user = payload["sub"]
    db_user = db.query(User).filter(User.email == current_user).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user not found"
        )
    if db_user and db_user.role == 'customer':
        baskets = db_user.basket 
        prods_list = []
        for item in baskets:
            prod = db.query(Products).filter(Products.id == item.product_id).first()
            if prod:
                prods_list.append({
                    'name':prod.name,
                    'price':prod.price,
                    'quantity':item.quantity,
                    'prod_img':f"{request.url.scheme}://{request.url.netloc}/images/{prod.prod_img}"
                })
        return prods_list