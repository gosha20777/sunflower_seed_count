# FROM python:3.7
FROM anibali/pytorch:latest

USER root

# WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# RUN pip install -U torch==1.4+cu100 torchvision==0.5+cu100 -f https://download.pytorch.org/whl/torch_stable.html
RUN apt update && apt install -y build-essential libgl1-mesa-glx libgtk2.0-dev && \
    pip install opencv-python && \
    python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.5/index.html

COPY . ./app
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000