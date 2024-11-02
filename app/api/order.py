from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.database import get_db
from app.models import User, Products, Basket, Order
from app.api.login_register import oauth2_scheme, verify_token
from sqlalchemy.orm import Session
from app.schemas import Changed, OrderCancel, OrderGet
from pprint import pprint
router = APIRouter(prefix="/order", tags=["ORDER"])


@router.post(
    "/add",response_model=Changed, status_code=status.HTTP_201_CREATED, dependencies=[Depends(oauth2_scheme)]
)
async def order(request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    current_user = payload["sub"]
    db_user = db.query(User).filter(User.email == current_user).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user not found"
        )
    if db_user and db_user.role == "customer":
        global new_order
        new_order = Order(
            customer_id = db_user.id,
            status = 'pending',
            total_amount = 0,
        )
        new_order.total_amount = new_order.calculate_total_amount(db)
        db.add(new_order)
        db.commit()
    if db_user.role == "seller":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user is seller"
        )
    
    return {'message':'created'}
@router.get('',response_model=list[OrderGet], status_code=status.HTTP_200_OK, dependencies=[Depends(oauth2_scheme)])
async def basket_get(request:Request, db:Session= Depends(get_db)):
    payload = verify_token(request)
    current_user = payload["sub"]
    db_user = db.query(User).filter(User.email == current_user).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user not found"
        )
    if db_user and db_user.role == "customer":
        orders = db.query(Order).filter(Order.customer_id == db_user.id).all()
        order_list = []
        if not orders:
            return []        
        for order in orders:
            if order:
                order_list.append({
                    'id':order.id,
                    'status':str(order.status.value),
                    'total_amount':order.total_amount
                })
        pprint(order_list)
        return order_list
@router.patch('/cancel/{order_id}', response_model=OrderCancel, dependencies=[Depends(oauth2_scheme)])
async def cancel(order_id:int, db:Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.status = 'cancelled'
    db.commit()
    return {'order_id':order.id, 'status':str(order.status.value)}
