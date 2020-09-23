import json
from PIL import Image
import base64
import os

basedir = "/home/gosha20777/files/datasets/sunflower_data/images/train"
files = os.listdir(basedir)

for file_name in files:
    if 'json' not in file_name:
        continue

    print(file_name)
    base_mane = os.path.basename(file_name).split('.')[0]
    json_name = os.path.join(basedir, file_name)
    img_name = os.path.join(basedir, f'{base_mane}.jpg')
    
    res_points = []
    text = open(json_name).read()
    img = Image.open(img_name)
    w, h = img.size
    print(h, w)
    with open(img_name, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    res = {
        "version": "4.2.9",
        "flags": {},
        "shapes": [],
        "imagePath": "..\\20190731_092735.jpg",
        "imageData": encoded_string.decode()
    }
    input_json = json.loads(text)

    for polygon in input_json:
        res_points = []
        points = polygon["data"]

        if len(points) < 3:
            print('incorrect polygon')
            continue
        for point in points:
            x = h - point['x'] * h
            y = point['y'] * w
            p_list = []
            p_list.append(y)
            p_list.append(x)
            res_points.append(p_list)
    
        shape = {
            "label": "1",
            "points": res_points,
            "group_id": None,
            "shape_type": "polygon",
            "flags": {}
        }
        res['shapes'].append(shape)
    
    json.dump(res, open(json_name, 'w'))
    print('ok')