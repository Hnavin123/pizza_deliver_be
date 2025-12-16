
# from fastapi import APIRouter, Depends, HTTPException
# from fastapi_jwt_auth import AuthJWT
# from sqlalchemy.orm import Session
# from fastapi.encoders import jsonable_encoder
# from models import User, Order
# from schemas import OrderModel
# from database import SessionLocal, engine

# order_router = APIRouter(
#     prefix='/orders'
# )

# # Dependency for DB session per request
# def get_db():
#     db = SessionLocal(bind=engine)
#     try:
#         yield db
#     finally:
#         db.close()

# # Test route
# @order_router.get("/")
# async def hello(Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required()
#         return {"message": "Hello! You're authorized to access orders."}
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=f"JWT error: {str(e)}")

# # Place an order
# @order_router.post('/order', status_code=201)
# async def place_an_order(
#     order: OrderModel, 
#     Authorize: AuthJWT = Depends(),
#     db: Session = Depends(get_db)
# ):
#     try:
        
#         Authorize.jwt_required()
#         current_user = Authorize.get_jwt_subject()
#         print(current_user)

        
#         user = db.query(User).filter(User.username == current_user).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

        
#         new_order = Order(
#             quantity=order.quantity,
#             pizza_size=order.pizza_size,
#             # user=user
#         )
#         new_order.user=user
#         db.add(new_order)
#         db.commit()
#         # db.refresh(new_order)

#         response = {
#             "pizza_size": new_order.pizza_size,
#             "quantity": new_order.quantity,
#             "id": new_order.id,
#             "order_status": new_order.order_status
#         }
        

#         return jsonable_encoder(response)

#     except HTTPException as he:
#         # Re-raise known HTTP exceptions
#         print(f"exception as {he}")
#     except Exception as e:
#         # Catch-all for debugging
#         print(f"[DEBUG] Error placing order: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from models import User, Order
from schemas import OrderModel
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
        print("➡️ Checking JWT...")
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        print("✅ JWT OK | Current user:", current_user)

        # Fetch user
        print("➡️ Fetching user from DB...")
        user = db.query(User).filter(User.username == current_user).first()
        print("User object:", user)

        if not user:
            print("❌ User not found")
            raise HTTPException(status_code=404, detail="User not found")

        # Pizza size mapping
        print("➡️ Validating pizza size...")
        PIZZA_SIZE_MAP = {
            "SMALL": "SMALL",
            "MEDIUM": "MEDIUM",
            "LARGE": "LARGE",
            "EXTRA-LARGE": "EXTRA-LARGE",
        }

        pizza_size = order.pizza_size
        print("Pizza size received:", pizza_size)

        if pizza_size not in PIZZA_SIZE_MAP:
            print("❌ Invalid pizza size")
            raise HTTPException(status_code=400, detail="Invalid pizza size")

        # Create order
        print("➡️ Creating Order object...")
        new_order = Order(
            quantity=order.quantity,
            pizza_size=PIZZA_SIZE_MAP[pizza_size],
            user=user
        )

        print("Order before commit:", new_order)

        # DB commit
        print("➡️ Saving to database...")
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        print("✅ Order saved successfully | ID:", new_order.id)

        # Serialize response
        response = {
            # "id": new_order.id,
            "quantity": new_order.quantity,
            "pizza_size": new_order.pizza_size.code,
            "order_status": new_order.order_status.code
        }

        print("➡️ Response payload:", response)
        print("================ REQUEST COMPLETED ================\n")

        return jsonable_encoder(response)

    except HTTPException as he:
        print("❌ HTTPException:", he.detail)
        raise he

    except Exception as e:
        print("🔥 UNEXPECTED ERROR OCCURRED")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))









# @order_router.get('/orders')
# async def list_all_orders(Authorize:AuthJWT=Depends()):
#     try:
#         Authorize.jwt_required()
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     current_user = Authorize.get_jwt_subject()
#     user = session.query(User).filter(User.username == current_user).first()
    