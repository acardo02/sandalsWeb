from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.db.connection import init_db
from app.routes import (
    users_routes,
    auth_routes,
    products_routes,
    order_routes,
    upload_routes,
    coupon_routes,
    review_routes,
    wishlist_routes,
    webhook_routes
)
from app.core.config import settings
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Crear app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para tienda en línea de productos artesanales",
    version="1.0.0"
)

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS
origins = settings.CORS_ORIGINS.split(",")

# En desarrollo, agregar orígenes comunes
if settings.ENVIRONMENT == "development":
    dev_origins = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]
    origins = list(set(origins + dev_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()



app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(users_routes.router, prefix="/users", tags=["Users"])
app.include_router(products_routes.router, prefix="/products", tags=["Products"])
app.include_router(order_routes.router, prefix="/orders", tags=["Orders"])
app.include_router(upload_routes.router, prefix="/upload", tags=["Uploads"])
app.include_router(coupon_routes.router, prefix="/coupons", tags=["Coupons"])
app.include_router(review_routes.router, prefix="/reviews", tags=["Reviews"])
app.include_router(wishlist_routes.router, prefix="/wishlist", tags=["Wishlist"])
app.include_router(webhook_routes.router, prefix="/webhooks", tags=["Webhooks"])
