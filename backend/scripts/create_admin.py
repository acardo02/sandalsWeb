"""
Script para crear el usuario administrador inicial.

Uso:
    python -m scripts.create_admin

IMPORTANTE: Este script debe ejecutarse solo UNA VEZ para crear el admin inicial.
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path para poder importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.user_model import User
from app.core.security import get_password_hash
from app.db.connection import init_db


async def create_admin():
    """Crea el usuario administrador inicial."""
    print("🔧 Inicializando conexión a la base de datos...")
    await init_db()

    print("\n📝 Crear usuario administrador")
    print("-" * 50)

    email = input("Email del administrador: ")
    password = input("Contraseña (mínimo 8 caracteres): ")
    first_name = input("Nombre: ")
    last_name = input("Apellido: ")
    phone_number = input("Teléfono: ")

    # Validar que la contraseña cumpla requisitos
    if len(password) < 8:
        print("❌ Error: La contraseña debe tener al menos 8 caracteres")
        return

    # Verificar si el email ya existe
    existing = await User.find_one(User.email == email)
    if existing:
        print(f"❌ Error: Ya existe un usuario con el email {email}")
        return

    # Crear usuario admin
    hashed_password = get_password_hash(password)
    admin_user = User(
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        role="admin",
        is_active=True
    )

    await admin_user.create()
    print(f"\n✅ Usuario administrador creado exitosamente: {email}")
    print(f"🔑 Rol: admin")
    print(f"\n⚠️  IMPORTANTE: Cambia la variable ALLOW_ADMIN_CREATION a 'false' en tu archivo .env")


if __name__ == "__main__":
    asyncio.run(create_admin())
