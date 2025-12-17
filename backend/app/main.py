from fastapi import FastAPI
from app.db.connection import init_db
from app.routes import users_routes, auth_routes

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(users_routes.router, prefix="/users", tags=["Users"])
