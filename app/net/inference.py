import torch
import torchvision
import detectron2
import numpy as np
import cv2
import matplotlib.pyplot as plt

# import some common detectron2 utilities
# from detectron2 import model_zoo
# from detectron2.utils.logger import setup_logger
# from detectron2.engine import DefaultPredictor
# from detectron2.config import get_cfg
# from detectron2.utils.visualizer import Visualizer
# from detectron2.data import MetadataCatalog
# from detectron2.engine import DefaultTrainer
# from detectron2.utils.visualizer import ColorMode
from pycocotools import mask
from skimage import measure
from datetime import datetime
import os

from app.net.config_net import RESIZE, device


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
    scale = compute_resize_scale(
        img.shape,
        min_side=min_side,
        max_side=max_side)

    # resize the image with the computed scale
    img = cv2.resize(img, None, fx=scale, fy=scale)

    return img, scale


def predict_from_img_in_coco_notation(predictor, img):
    print("Detecting START")
    img_bytes_ = np.load(img + ".npy")
    im = cv2.imdecode(np.frombuffer(img_bytes_, np.uint8), 1)
    # im = cv2.imread(img)
    if RESIZE:
        im, scale = resize_image(im)
    print(f"detecting {img}")

    outputs: Instances = predictor(im)["instances"]
    annotation = create_coco_annotation(outputs, img)
    print("Detecting END")
    return annotation


def get_ground_truth_area(ground_truth_binary_mask):
    """
    Args
        bitmask: A bitmask obtained from the predictions of the model.
    Returns
        Segmentation area
    """
    fortran_ground_truth_binary_mask = np.asfortranarray(
        ground_truth_binary_mask)
    encoded_ground_truth = mask.encode(fortran_ground_truth_binary_mask)
    ground_truth_area = mask.area(encoded_ground_truth)
    return ground_truth_area.item()


def get_segmentation_from_bitmask(bitmask):
    """ Getting a list of segmentation in polygon format
    Args
        bitmask: A bitmask obtained from the predictions of the model.
    Returns
        List of segmentation.
    """

    contours = measure.find_contours(bitmask, 0.5)
    seg = []
    for contour in contours:
        contour = np.flip(contour, axis=1)
        segmentation = contour.ravel().tolist()
        seg.append(segmentation)
    return seg


def create_coco_annotation(outputs_prediction, filename):
    """ Returns the COCO annotation from the model prediction.
    Args
        outputs_prediction: Prediction of model.
    Returns
        Dict COCO annotation.
    """

    image_height = outputs_prediction.image_size[0]
    image_width = outputs_prediction.image_size[1]

    boxes = (
        outputs_prediction
        .get_fields()["pred_boxes"]
        .tensor.to(device)
        .numpy()
    )

    # categories = (
    #         outputs_prediction
    #         .get_fields()["pred_classes"]
    #         .to(device)
    #         .numpy()
    #     )

    masks = (
        outputs_prediction
        .get_fields()["pred_masks"]
        .to(device)
        .numpy()
    )

    annotation = {}
    annotation['info'] = {
        "description": None,
        "url": None,
        "version": None,
        "year": datetime.today().year,
        "contributor": None,
        "date_created": '{date:%Y-%m-%d %H:%M:%S}'.format(date=datetime.now())}

    annotation["licenses"] = [
        {
            "url": None,
            "id": 0,
            "name": None
        }
    ]

    annotation["images"] = [
        {
            "license": 0,
            "url": None,
            "file_name": filename,
            "height": image_height,
            "width": image_width,
            "date_captured": None,
            "id": 0
        }
    ]

    annotation["annotations"] = []

    for i, box in enumerate(boxes):
        data = {}
        data["id"] = i
        data["image_id"] = 0
        data["category_id"] = 1
        data["segmentation"] = get_segmentation_from_bitmask(masks[i])
        data["area"] = get_ground_truth_area(masks[i])
        data["iscrowd"] = 0
        annotation["annotations"].append(data)

    annotation["categories"] = [
        {
            "supercategory": None,
            "id": 0,
            "name": "_background_"
        },
        {
            "supercategory": None,
            "id": 1,
            "name": "sunflower_seed"
        }
    ]

    return annotation
