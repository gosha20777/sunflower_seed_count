# import subprocess
# import os
# from subprocess import TimeoutExpired
# from config import EXECUTER, TIMEOUT

from app.net.inference import predict_from_img_in_coco_notation
from app.net.config_net import PREDICTOR

predictor = PREDICTOR


def run_task(qeue_name, path_save):
    outputs = predict_from_img_in_coco_notation(predictor, path_save)
    return outputs
