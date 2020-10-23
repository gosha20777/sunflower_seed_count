
# from starlette.status import HTTP_400_BAD_REQUEST
import os
import json
from urllib.parse import urlparse
import numpy as np
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, File, UploadFile

import rq
from rq import Queue
from rq.job import Job
from redis import Redis
from rq import use_connection

import requests
import app.workers.worker as worker

import dill

from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, STORAGE_PATH


resdis_connection = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
use_connection(resdis_connection)
# queue = Queue(RQ_QUEUES, connection=resdis_connection, serializer=dill)

# Folder storage path
base_dir = os.path.relpath(os.path.dirname(__file__ + "/../../../../../"))
storage_path = STORAGE_PATH
folder_storage = os.path.join(base_dir, storage_path)

with open(os.path.join(base_dir, "app/core/config.json")) as config_file:
    models_conf = json.load(config_file)

# Загрузить информацию о всех очередях
rq_queues = {}
for model in models_conf.keys():
    queue_name = models_conf[model]['queue_name']
    rq_queues[queue_name] = Queue(queue_name, serializer=dill)


# print(rq_queues)
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


@router.post("/{queue_name}/push/image/")
async def upload_image_from_local(queue_name, file: UploadFile = File(...)):
    """ Accepts queue name and file, executes job, and returns job_id.
    Args
        queue_name: Name of the queue running in worker.
        file: Image file.
    Returns
        job_id: In format {"job_id": "id"}
    """

    if queue_name not in rq_queues.keys():
        raise HTTPException(status_code=404, detail="This queue not found")

    content = await file.read()

    path_save = save_image_in_npy(content, file.filename)

    job = rq_queues[queue_name].enqueue(
        worker.run_task,
        path_save
    )

    return {"job_id": job.id}


@router.post("/{queue_name}/push/url/")
def upload_image_from_url(queue_name: str, url_images: UrlImages):
    """ Accepts queue name and file, executes job, and returns job_id.
    Args
        queue_name: Name of the queue running in worker.
        url: The URL of the image.
    Returns
        job_id: In format {"job_id": "id"}
    """
    if queue_name not in rq_queues.keys():
        raise HTTPException(status_code=404, detail="This queue not found")

    url = url_images.url
    content = requests.get(url).content

    url = urlparse(url)
    filename = os.path.basename(url.path)
    
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Must be .jpg, .jpeg, .png, or .BMP format.")

    path_save = save_image_in_npy(content, filename)

    job = rq_queues[queue_name].enqueue(
        worker.run_task,
        path_save
    )

    return {"job_id": job.id}


@router.post("/{queue_name}/push/fs/")
def upload_image_from_fs(queue_name: str, fs: FSImages):
    """ Accepts queue name and path in the file system, executes job, and returns job_id.
    Args
        queue_name: Name of the queue running in worker.
        fs: Path in the file system.
    Returns
        job_id: In format {"job_id": "id"}
    """

    if queue_name not in rq_queues.keys():
        raise HTTPException(status_code=404, detail="This queue not found")

    fs_path = fs.fs_path

    with open(fs_path, 'rb') as file:
        content = file.read()

    filename = os.path.basename(fs_path)

    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Must be .jpg, .jpeg, .png, or .BMP format.")

    path_save = save_image_in_npy(content, filename)

    job = rq_queues[queue_name].enqueue(
        worker.run_task,
        path_save
    )

    return {"job_id": job.id}


@router.get("/{queue_name}/pop/{task_id}")
def get_im(task_id: str):
    """ Accepts queue name and task_id (job_id) and returns the image annotation in COCO format.
    Args
        queue_name: Name of the queue running in worker.
        task_id: Job id in the queue.
    Returns
        COCO Image annotation in json format.
    """
    try:
        job = Job.fetch(task_id, connection=resdis_connection, serializer=dill)
        # print("Job_result", job.result)
        if job.result is None:
            return {'status': job.get_status()}

        result = job.result

        return result

    except rq.exceptions.NoSuchJobError:
        return {'status': 'no such job'}
    except RuntimeError as ex:
        return {'error': ex}
