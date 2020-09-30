# from fastapi import FastAPI, Depends, HTTPException
# from starlette.status import HTTP_400_BAD_REQUEST

# # from app.api.dependencies.authentication import get_current_user_authorizer
# # from app.api.dependencies.database import get_repository
# # from app.api.dependencies.profiles import get_profile_by_username_from_path
# # from app.db.repositories.profiles import ProfilesRepository
# # from app.models.domain.profiles import Profile
# # from app.models.domain.users import User
# # from app.models.schemas.profiles import ProfileInResponse
# # from app.resources import strings

# curl -d '{"url":"value1"}' -H "Content-Type: application/json" -X POST http://localhost:8000/qeue_name/push/url/

# curl -X POST -H "Content-Type: multipart/form-data" -F "file=@20190731_092735.jpg" http://localhost:8000/api/v1/qeue_name/push/image/

from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, File, UploadFile

# app = FastAPI()


class UrlImages(BaseModel):
    url: str

class FSImages(BaseModel):
    fs: str

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

router = FastAPI()

@router.get("/")
async def read_root():
    return {"Hello": "World"}

@router.post("/{qeue_name}/push/image/")
def upload_image_from_local(file: UploadFile = File(...)):
    # print(len(file))
    print(file.content_type)
    return {"status": 200}

@router.post("/{qeue_name}/push/url/")
def upload_image_from_url(url_images: UrlImages):
    # params = url_images
    # print()
    return {"job": url_images.url}

@router.post("/{qeue_name}/push/fs/")
def upload_image_from_fs(fs: FSImages):
    return {"status": 200}

# @router.post("/items/{item_id}")
# async def create_item(item_id: int, item: Item):
#     return {"item_id": item_id, **item.dict()}

# @router.post("/items/{item_id}")
# async def create_item(item_id: int):
#     return {"item_id": item_id}

# @router.get("/items/")
# async def create_item():
#     return {"item_id": "item_id"}