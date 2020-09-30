# import subprocess
# import os
# from subprocess import TimeoutExpired
# from config import EXECUTER, TIMEOUT

from app.net.inference import predict_from_img
from app.net.config_net import PREDICTOR

predictor = PREDICTOR

def run_task(qeue_name, path_save):
    outputs = predict_from_img(predictor, path_save)
    return outputs