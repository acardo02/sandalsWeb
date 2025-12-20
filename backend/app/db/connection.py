from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user_model import User
from app.models.product_model import Product
from app.models.orders_model import Order

client: AsyncIOMotorClient | None = None

async def init_db():
    global client
    client = AsyncIOMotorClient(settings.MONGO_URL)

    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[
            User,
            Product,
            Order
        ]
    )

    print("✅ MongoDB conectado correctamente")