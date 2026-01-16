"""
Rutas para subir imágenes a Cloudinary
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
import cloudinary
import cloudinary.uploader
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user_model import User

router = APIRouter()

# Configurar Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


@router.post("/")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Sube una imagen a Cloudinary y retorna la URL.

    Solo usuarios autenticados pueden subir imágenes.
    """
    # Validar que sea una imagen
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen (jpg, png, webp, etc.)"
        )

    # Validar tamaño (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen no puede superar los 10MB"
        )

    try:
        # Subir a Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder="sandals_products",  # Carpeta en Cloudinary
            resource_type="image",
            transformation=[
                {"quality": "auto:good"},  # Optimizar calidad
                {"fetch_format": "auto"}   # Formato automático (webp si lo soporta)
            ]
        )

        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format")
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir imagen: {str(e)}"
        )


@router.delete("/{public_id:path}")
async def delete_image(
    public_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una imagen de Cloudinary.

    Solo admins pueden eliminar imágenes.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden eliminar imágenes"
        )

    try:
        result = cloudinary.uploader.destroy(public_id)

        if result.get("result") == "ok":
            return {"message": "Imagen eliminada correctamente"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Imagen no encontrada"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar imagen: {str(e)}"
        )
