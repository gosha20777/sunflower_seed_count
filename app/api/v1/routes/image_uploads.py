
# from starlette.status import HTTP_400_BAD_REQUEST
# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import JSONResponse

# from app.api.dependencies.authentication import get_current_user_authorizer
# from app.api.dependencies.database import get_repository
# from app.api.dependencies.profiles import get_profile_by_username_from_path
# from app.db.repositories.profiles import ProfilesRepository
# from app.models.domain.profiles import Profile
# from app.models.domain.users import User
# from app.models.schemas.profiles import ProfileInResponse
# from app.resources import strings

# from PIL import Image



# import io
import os
import json
from urllib.parse import urlparse
import numpy as np
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile

import rq
import requests
from rq import Queue, Worker
from rq.job import Job
from redis import Redis
import app.workers.worker as worker

import dill

from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, RQ_QUEUES, STORAGE_PATH


resdis_connection = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
queue = Queue(RQ_QUEUES, connection=resdis_connection, serializer=dill)


# Folder storage path
base_dir = os.path.relpath(os.path.dirname(__file__ + "/../../../../../"))
storage_path = STORAGE_PATH
folder_storage = os.path.join(base_dir, storage_path)

# uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
# print(uppath(__file__, 4))

# if not os.path.exists(storage_path):
#     os.makedirs(storage_path)


class UrlImages(BaseModel):
    url: str


class FSImages(BaseModel):
    fs_path: str


router = APIRouter()


@router.get("/")
async def root():
    return {"message": "API version 0.0.0"}


def save_image_in_npy(content, filename):
    '''
    Save image in .npy format and return saving path
    '''
    path_save = os.path.join(folder_storage, filename)
    np.save(path_save, content)
    return path_save


@router.post("/{qeue_name}/push/image/")
async def upload_image_from_local(qeue_name: str, file: UploadFile = File(...)):
    content = await file.read()

    path_save = save_image_in_npy(content, file.filename)

    job = queue.enqueue(
        worker.run_task,
        qeue_name,
        path_save,
        job_id='my_job_id'
    )

    return {"job_id": job.id}


@router.post("/{qeue_name}/push/url/")
def upload_image_from_url(url_images: UrlImages):
    url = url_images.url
    content = requests.get(url).content

    url = urlparse(url)
    filename = os.path.basename(url.path)

    path_save = save_image_in_npy(content, filename)

    job = queue.enqueue(
        worker.run_task,
        qeue_name,
        path_save,
        job_id='my_job_id'
    )

    return {"job_id": job.id}


@router.post("/{qeue_name}/push/fs/")
def upload_image_from_fs(fs: FSImages):
    fs_path = fs.fs_path

    with open(fs_path, 'rb') as f:
        content = f.read()

    filename = os.path.basename(fs_path)

    path_save = save_image_in_npy(content, filename)

    job = queue.enqueue(
        worker.run_task,
        qeue_name,
        path_save,
        job_id='my_job_id'
    )

    return {"job_id": job.id}


@router.get("/{queue_name}/pop/{task_id}")
def get_im(task_id: str):
    try:
        job = Job.fetch(task_id, connection=resdis_connection, serializer=dill)
        # print("Job_result", job.result)
        if job.result is None:
            return {'status': job.get_status()}
        out = job.result

        return out

    except rq.exceptions.NoSuchJobError:
        return {'status': 'no such job'}
    except RuntimeError as ex:
        return {'error': ex}
