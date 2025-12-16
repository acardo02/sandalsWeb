from fastapi import FastAPI
from app.db.connection import init_db
from app.routes.users_routes import router as users_router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(users_router)