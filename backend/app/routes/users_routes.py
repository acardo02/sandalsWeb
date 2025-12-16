from fastapi import APIRouter
from app.models.user_model import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
async def create_user(user: User):
    await user.insert()
    return user

@router.get("/")
async def get_users():
    return await User.find_all().to_list()