import torch, torchvision
import detectron2
from detectron2.utils.logger import setup_logger
import numpy as np
import cv2
import matplotlib.pyplot as plt

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
from detectron2.utils.visualizer import ColorMode
from datetime import datetime
import os
import argparse

def compute_resize_scale(image_shape, min_side=800, max_side=1333):
    """ Compute an image scale such that the image size is constrained to min_side and max_side.
    Args
        min_side: The image's min side will be equal to min_side after resizing.
        max_side: If after resizing the image's max side is above max_side, resize until the max side is equal to max_side.
    Returns
        A resizing scale.
    """
    (rows, cols, _) = image_shape

    smallest_side = min(rows, cols)

    # rescale the image so the smallest side is min_side
    scale = min_side / smallest_side

    # check if the largest side is now greater than max_side, which can happen
    # when images have a large aspect ratio
    largest_side = max(rows, cols)
    if largest_side * scale > max_side:
        scale = max_side / largest_side

    return scale

def resize_image(img, min_side=800, max_side=1333):
    """ Resize an image such that the size is constrained to min_side and max_side.
    Args
        min_side: The image's min side will be equal to min_side after resizing.
        max_side: If after resizing the image's max side is above max_side, resize until the max side is equal to max_side.
    Returns
        A resized image.
    """
    # compute scale to resize the image
    scale = compute_resize_scale(img.shape, min_side=min_side, max_side=max_side)

    # resize the image with the computed scale
    img = cv2.resize(img, None, fx=scale, fy=scale)

    return img, scale

def parse_args(args):
    parser = argparse.ArgumentParser(description='run inference')
    parser.add_argument(
        '--img',
        help='path to image',
        type=str,
        required=True
    )
    parser.add_argument(
        '--bin',
        help='path to inference model',
        type=str,
        required=True
    )
    parser.add_argument(
        '--topk',
        help='top k polygons count',
        type=int,
        required=False,
        default=5000
    )
    parser.add_argument(
        '--resize',
        help='resize image',
        action='store_true',
        required=False,
    )
    parser.add_argument(
        '--cpu',
        help='use cpu only inference',
        action='store_true',
        required=False,
    )
    return parser.parse_args(args)

def main(args=None):
    args=parse_args(args)

    print(f"init pytorch: {torch.__version__}")
    
    setup_logger()
    
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.DATALOADER.NUM_WORKERS = 16
    cfg.MODEL.WEIGHTS = args.bin
    cfg.SOLVER.IMS_PER_BATCH = 8
    cfg.SOLVER.BASE_LR = 0.00025
    cfg.SOLVER.MAX_ITER = 500
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5 
    cfg.MODEL.RPN.PRE_NMS_TOPK_TEST = args.topk
    cfg.MODEL.RPN.POST_NMS_TOPK_TEST = args.topk
    cfg.TEST.DETECTIONS_PER_IMAGE = args.topk
    if args.cpu:
        cfg.MODEL.DEVICE = 'cpu'

    predictor = DefaultPredictor(cfg)

    im = cv2.imread(args.img)
    if args.resize:
        im, scale = resize_image(im)
    print(f"detecting {args.img}")
    start = datetime.now()
    outputs = predictor(im)
    v = Visualizer(im[:, :, ::-1], 
                   scale=0.8, 
                   instance_mode=ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels
    )
    v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    print(f"done at: {datetime.now() - start} s")
    result = v.get_image()[:, :, ::-1]
    f_name = args.img + '.out.jpg'
    cv2.imwrite(f_name, result)
    print(f"visualisation saved to {f_name}")

if __name__ == '__main__':
    main()