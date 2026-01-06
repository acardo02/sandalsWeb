import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from app.core.config import settings

cloudinary.config( 
    cloud_name = settings.CLOUDINARY_CLOUD_NAME, 
    api_key = settings.CLOUDINARY_API_KEY, 
    api_secret = settings.CLOUDINARY_API_SECRET 
)

def upload_image(file: UploadFile):
   if not file.content_type.startswith("image/"):
      raise HTTPException(
         status_code=400,
         detail="El archivo debe de ser una imagen"
      )
   
   try:
      response = cloudinary.uploader.upload(
         file.file,
         folder = "calero",
         resource_type="image"
      )
      return response.get("secure_url")
   except Exception as e:
      raise HTTPException(
         status_code=500,
         detail=f"Error al subir a Cloudinary: {str(e)}"
      )