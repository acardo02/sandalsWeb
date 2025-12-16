from beanie import Document
from pydantic import Field
from typing import Optional

class User(Document):
    name: str
    email: str
    age: Optional[int] = None

    class Settings:
        name = "users"  # nombre de la colección
