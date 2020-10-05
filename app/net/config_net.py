from detectron2.utils.logger import setup_logger
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import torch

TOPK = 5000
RESIZE = True
setup_logger()

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file(
    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.DATALOADER.NUM_WORKERS = 16
cfg.MODEL.WEIGHTS = "snapshots/model_v1.0.pth"
cfg.SOLVER.IMS_PER_BATCH = 8
cfg.SOLVER.BASE_LR = 0.00025
cfg.SOLVER.MAX_ITER = 500
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg.MODEL.RPN.PRE_NMS_TOPK_TEST = TOPK
cfg.MODEL.RPN.POST_NMS_TOPK_TEST = TOPK
cfg.TEST.DETECTIONS_PER_IMAGE = TOPK

device = 'cuda' if torch.cuda.is_available() else 'cpu'
cfg.MODEL.DEVICE = device

PREDICTOR: DefaultPredictor = DefaultPredictor(cfg)
