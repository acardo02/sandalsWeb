from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "message": "Upload endpoint funcionando"
    }
