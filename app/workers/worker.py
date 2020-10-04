from app.net.inference import predict_from_img_in_coco_notation
from app.net.config_net import PREDICTOR

predictor = PREDICTOR


def run_task(path_save):
    outputs = predict_from_img_in_coco_notation(predictor, path_save)
    return outputs
