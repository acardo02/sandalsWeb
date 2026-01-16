from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user_model import User
from app.models.product_model import Product
from app.models.orders_model import Order
from app.models.coupon_model import Coupon
from app.models.review_model import ProductReview
from app.models.wishlist_model import Wishlist
from app.models.shipping_model import ShippingZone

client: AsyncIOMotorClient | None = None

async def init_db():
    global client
    client = AsyncIOMotorClient(settings.MONGO_URL)

    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[
            User,
            Product,
            Order,
            Coupon,
            ProductReview,
            Wishlist,
            ShippingZone
        ]
    )

    print("[OK] MongoDB conectado correctamente con todos los modelos")