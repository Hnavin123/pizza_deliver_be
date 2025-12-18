from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from database import SessionLocal, engine
import traceback

order_router = APIRouter(prefix="/orders")


# Dependency for DB session
def get_db():
    db = SessionLocal(bind=engine)
    try:
        yield db
    finally:
        db.close()


@order_router.post("/order", status_code=201)
async def place_an_order(
    order: OrderModel,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    print("\n================ NEW ORDER REQUEST ================")
    print("Incoming payload:", order.dict())

    try:
        # JWT
        print(" Checking JWT...")
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        print(" JWT OK | Current user:", current_user)

        # Fetch user
        print(" Fetching user from DB...")
        user = db.query(User).filter(User.username == current_user).first()
        print("User object:", user)

        if not user:
            print(" User not found")
            raise HTTPException(status_code=404, detail="User not found")

        # Pizza size mapping
        print(" Validating pizza size...")
        PIZZA_SIZE_MAP = {
            "SMALL": "SMALL",
            "MEDIUM": "MEDIUM",
            "LARGE": "LARGE",
            "EXTRA-LARGE": "EXTRA-LARGE",
        }

        pizza_size = order.pizza_size.upper()
        print("Pizza size received:", pizza_size)

        if pizza_size not in PIZZA_SIZE_MAP:
            print(" Invalid pizza size")
            raise HTTPException(status_code=400, detail="Invalid pizza size")

        # Create order
        print(" Creating Order object...")
        new_order = Order(
            quantity=order.quantity,
            pizza_size=PIZZA_SIZE_MAP[pizza_size],
            user=user
        )

        print("Order before commit:", new_order)

        # DB commit
        print(" Saving to database...")
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        # print(" Order saved successfully | ID:", new_order.id)

        # Serialize response
        response = {
            # "id": new_order.id,
            "quantity": new_order.quantity,
            "pizza_size": new_order.pizza_size,
            "order_status": new_order.order_status
        }

        print(" Response payload:", response)
        print("================ REQUEST COMPLETED ================\n")

        return jsonable_encoder(response)

    except HTTPException as he:
        print(" HTTPException:", he.detail)
        raise he

    except Exception as e:
        print(" UNEXPECTED ERROR OCCURRED")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@order_router.get("/orders", status_code=status.HTTP_200_OK)
def list_all_orders(
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)  # preferred way
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

    current_user = Authorize.get_jwt_subject()

    user = db.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view all orders"
        )

    orders = db.query(Order).all()
    return jsonable_encoder(orders)

@order_router.get('/orders/{id}')
async def get_order_by_id(
    id: int,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

    current_user = Authorize.get_jwt_subject()

    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to view this order"
        )

    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return jsonable_encoder(order)

    
    
@order_router.get('/user/orders')
async def get_user_orders(
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

    current_user = Authorize.get_jwt_subject()

    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    orders = db.query(Order).filter(Order.user_id == user.id).all()

    return jsonable_encoder(orders)


@order_router.get('/user/order/{id}', response_model=OrderModel)
async def get_specific_order(
    id: int,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

    current_user = Authorize.get_jwt_subject()

    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    order = (
        db.query(Order)
        .filter(Order.id == id, Order.user_id == user.id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order


@order_router.put('/order/update/{order_id}')
async def update_order(
    order_id: int,
    order: OrderModel,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

    current_user = Authorize.get_jwt_subject()

    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    order_to_update = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == user.id)
        .first()
    )

    if not order_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # update only provided fields
    if order.quantity is not None:
        order_to_update.quantity = order.quantity

    if order.pizza_size is not None:
        order_to_update.pizza_size = order.pizza_size

    db.commit()
    db.refresh(order_to_update)

    return jsonable_encoder(order_to_update)

    
    
    
@order_router.patch('/order/update/{order_id}')
async def update_order_status(
    order_id: int,
    order: OrderStatusModel,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

    current_user = Authorize.get_jwt_subject()

    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update order status"
        )

    order_to_update = db.query(Order).filter(Order.id == order_id).first()
    if not order_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order_to_update.order_status = order.order_status

    db.commit()
    db.refresh(order_to_update)

    return jsonable_encoder(order_to_update)

    
    
@order_router.delete('/order/delete/{order_id}', status_code=status.HTTP_200_OK)
async def delete_an_order(
    order_id: int,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

    current_user = Authorize.get_jwt_subject()

    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can delete orders"
        )

    order_to_delete = (db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
)
    if not order_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    db.delete(order_to_delete)
    db.commit()

    return {"message": "Order deleted successfully"}
