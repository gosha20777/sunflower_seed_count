# FROM python:3.7
# WORKDIR /app
FROM anibali/pytorch:latest

USER root
RUN pip install rq redis
RUN apt update && apt install -y build-essential libgl1-mesa-glx libgtk2.0-dev && \
    pip install opencv-python && \
    python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.5/index.html && \
    pip install scikit-image


COPY . app/
CMD rq worker --url redis://redis:6379 queue_sunflower