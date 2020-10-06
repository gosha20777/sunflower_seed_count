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

# curl -d '{"url":"value1"}' -H "Content-Type: application/json" -X POST
# http://localhost:8000/qeue_name/push/url/

# curl -X POST -H "Content-Type: multipart/form-data" -F "file=@20190731_092735.jpg" http://localhost:5000/api/v1/qeue_name/push/image/

import os
import cv2
import json
import requests
import numpy as np
from urllib.parse import urlparse
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, File, UploadFile


class UrlImages(BaseModel):
    url: str


class FSImages(BaseModel):
    fs: str


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}

folder_storage = "./"


def save_image_in_npy(content, filename):
    path_save = os.path.join(folder_storage, filename)
    np.save(path_save, content)
    return path_save


@app.post("/api/v1/{qeue_name}/push/image/")
async def upload_image_from_local(file: UploadFile = File(...)):
    content = await file.read()
    path_save = save_image_in_npy(content, file.filename)
    filename = file.filename
    # path_save = os.path.join(folder_storage, filename)
    # cv2.imwrite("cv2" + file.filename, decoded)

    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        return {"status": "NOT CORRECT ext."}

    return {"status": 200}


@app.post("/api/v1/{qeue_name}/push/url/")
def upload_image_from_url(url_images: UrlImages):
    url = url_images.url
    content = requests.get(url).content

    url = urlparse(url)
    filename = os.path.basename(url.path)

    path_save = save_image(content, filename)

    print(path_save)

    return {"job": filename}


@app.post("/api/v1/{qeue_name}/push/fs/")
def upload_image_from_fs(fs: FSImages):
    fs_path = fs.fs

    with open(fs_path, 'rb') as f:
        content = f.read()

    filename = os.path.basename(fs_path)

    path_save = save_image(content, filename)

    print(path_save)

    return {"status": 200}

