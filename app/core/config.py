# import logging
# import sys
from typing import List
# from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret
# from app.core.logging import InterceptHandler

API_PREFIX = "/api/v1"

# JWT_TOKEN_PREFIX = "Token"  # noqa: S105
VERSION = "0.0.0"

config = Config(".env")

DEBUG: bool = config("DEBUG", cast=bool, default=False)

REDIS_HOST: str = config("REDIS_HOST", default="redis")
REDIS_PORT: int = config("REDIS_PORT", cast=int, default=6379)
REDIS_DB: int = config("REDIS_DB", cast=int, default=0)
RQ_QUEUES = "queue_test" 

STORAGE_PATH = "storage"

# SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret)

PROJECT_NAME: str = config("PROJECT_NAME", default="App for segmentation sunflower's seed on images")
ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
)




# # logging configuration

# LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
# LOGGERS = ("uvicorn.asgi", "uvicorn.access")

# logging.getLogger().handlers = [InterceptHandler()]
# for logger_name in LOGGERS:
#     logging_logger = logging.getLogger(logger_name)
#     logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]

# logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])


