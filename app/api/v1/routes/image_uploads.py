from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from starlette.status import HTTP_400_BAD_REQUEST

# from app.api.dependencies.authentication import get_current_user_authorizer
# from app.api.dependencies.database import get_repository
# from app.api.dependencies.profiles import get_profile_by_username_from_path
# from app.db.repositories.profiles import ProfilesRepository
# from app.models.domain.profiles import Profile
# from app.models.domain.users import User
# from app.models.schemas.profiles import ProfileInResponse
# from app.resources import strings
from pydantic import BaseModel
# from PIL import Image
import numpy as np
import io
import os 


import app.workers.worker as worker
import json
from redis import Redis
from rq import Queue, Worker
from rq.job import Job
import rq
# from config import REDIS_HOST

from app.core.config import REDIS_HOST, STORAGE_PATH


resdis_connection = Redis(host=REDIS_HOST, port=6379, db=0)
queue = Queue('queue_test', connection=resdis_connection)

base_dir = os.path.relpath(os.path.dirname(__file__ + "/../../../../../" ))
storage_path = STORAGE_PATH
folder_storage = os.path.join(base_dir, storage_path)

# uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
# print(uppath(__file__, 4))

# if not os.path.exists(storage_path):
#     os.makedirs(storage_path)

class UrlImages(BaseModel):
    url: str

class FSImages(BaseModel):
    fs: str

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "API version 0.0.0"}


@router.post("/{qeue_name}/push/image/")
async def upload_image_from_local(qeue_name: str, file: UploadFile = File(...)):
    content = await file.read()
    np_content = np.frombuffer(content, dtype=np.uint8)
    path_save = os.path.join(folder_storage, file.filename)
    np.save(path_save, np_content)
    # with open(path_save, "wb+") as f:
    #     f.write(content)

    job = queue.enqueue(
            worker.run_task,
            qeue_name,
            path_save,
            job_id='my_job_id'
        )

    return {"job_id": job.id}


@router.post("/{qeue_name}/push/url/")
def upload_image_from_url(url_images: UrlImages):
    pass

@router.get("/{queue_name}/pop/{task_id}")
def get_im(task_id: str):
    try:     
        print("JOB_ID", task_id)
        job = Job.fetch(task_id, connection=resdis_connection)
        print(job.get_status())
        if job.result is None:
            return {'status': job.get_status()}
        out = job.result
        return {'result': out}
    
    except rq.exceptions.NoSuchJobError:
        return { 'status': 'no such job' }
    except RuntimeError as ex:
        return { 'error': ex }


@router.post("/{qeue_name}/push/fs/")
def upload_image_from_fs(fs: FSImages):
    pass


# @router.get(
#     "/{username}",
#     response_model=ProfileInResponse,
#     name="profiles:get-profile",
# )
# async def retrieve_profile_by_username(
#     profile: Profile = Depends(get_profile_by_username_from_path),
# ) -> ProfileInResponse:
#     return ProfileInResponse(profile=profile)


# @router.post(
#     "/{username}/follow",
#     response_model=ProfileInResponse,
#     name="profiles:follow-user",
# )
# async def follow_for_user(
#     profile: Profile = Depends(get_profile_by_username_from_path),
#     user: User = Depends(get_current_user_authorizer()),
#     profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
# ) -> ProfileInResponse:
#     if user.username == profile.username:
#         raise HTTPException(
#             status_code=HTTP_400_BAD_REQUEST,
#             detail=strings.UNABLE_TO_FOLLOW_YOURSELF,
#         )

#     if profile.following:
#         raise HTTPException(
#             status_code=HTTP_400_BAD_REQUEST,
#             detail=strings.USER_IS_ALREADY_FOLLOWED,
#         )

#     await profiles_repo.add_user_into_followers(
#         target_user=profile,
#         requested_user=user,
#     )

#     return ProfileInResponse(profile=profile.copy(update={"following": True}))


# @router.delete(
#     "/{username}/follow",
#     response_model=ProfileInResponse,
#     name="profiles:unsubscribe-from-user",
# )
# async def unsubscribe_from_user(
#     profile: Profile = Depends(get_profile_by_username_from_path),
#     user: User = Depends(get_current_user_authorizer()),
#     profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
# ) -> ProfileInResponse:
#     if user.username == profile.username:
#         raise HTTPException(
#             status_code=HTTP_400_BAD_REQUEST,
#             detail=strings.UNABLE_TO_UNSUBSCRIBE_FROM_YOURSELF,
#         )

#     if not profile.following:
#         raise HTTPException(
#             status_code=HTTP_400_BAD_REQUEST,
#             detail=strings.USER_IS_NOT_FOLLOWED,
#         )

#     await profiles_repo.remove_user_from_followers(
#         target_user=profile,
#         requested_user=user,
#     )

#     return ProfileInResponse(profile=profile.copy(update={"following": False}))