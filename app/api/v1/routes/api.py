from fastapi import APIRouter

from app.api.v1.routes import image_uploads

router = APIRouter()

router.include_router(image_uploads.router, tags=["image_uploads"])
