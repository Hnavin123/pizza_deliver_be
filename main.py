# from fastapi import FastAPI
# from order_routes import order_router
# from auth_routes import auth_router
# # from fastapi_jwt_auth_v2 import AuthJWT
# from fastapi_jwt_auth import AuthJWT


# from schemas import Settings
# app = FastAPI()

# @AuthJWT.load_config(settings_name="AuthJWT")
# def get_config():
#     return AuthJWT()

# app.include_router(order_router, tags=["orders"])
# app.include_router(auth_router, tags=["auth"])  



from fastapi import FastAPI
from order_routes import order_router
from auth_routes import auth_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings

app = FastAPI()

# Provide JWT config
@AuthJWT.load_config
def get_config():
    return Settings()

# Include routers
app.include_router(order_router, tags=["orders"])
app.include_router(auth_router, tags=["auth"])
