FROM anibali/pytorch

RUN sudo apt update && sudo apt install -y build-essential libgl1-mesa-glx libgtk2.0-dev && \
    pip install opencv-python && \
    python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.5/index.html

WORKDIR /app
COPY cli-inference.py .
CMD ['python', 'cli-inference.py']