import json
import os
import numpy as np
import glob
import PIL.Image


def labelme_to_coco(labelme_jsons, save_json_path):
    coco = {
        "info": {},
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": []
    }

    categories = {}
    category_id = 1
    annotation_id = 1

    for image_id, labelme_json in enumerate(labelme_jsons):
        with open(labelme_json, 'r') as f:
            data = json.load(f)

        # JSON 파일에서 이미지 크기 가져오기
        width = data['imageWidth']
        height = data['imageHeight']

        # 이미지 정보 추가
        image_info = {
            "id": image_id,
            "file_name": data['imagePath'],
            "width": width,
            "height": height
        }
        coco['images'].append(image_info)

        for shape in data['shapes']:
            label = shape['label']
            if label not in categories:
                categories[label] = category_id
                coco['categories'].append({
                    'id': category_id,
                    'name': label,
                    'supercategory': 'none'
                })
                category_id += 1

            points = shape['points']
            polygon = np.array(points).flatten().tolist()

            # 바운딩 박스 계산
            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_y = max(p[1] for p in points)
            bbox = [min_x, min_y, max_x - min_x, max_y - min_y]
            area = bbox[2] * bbox[3]

            annotation = {
                "id": annotation_id,
                "image_id": image_id,
                "category_id": categories[label],
                "segmentation": [polygon],
                "area": area,
                "bbox": bbox,
                "iscrowd": 0
            }
            coco['annotations'].append(annotation)
            annotation_id += 1

    with open(save_json_path, 'w') as f:
        json.dump(coco, f)


# 모든 LabelMe JSON 파일을 변환
labelme_jsons = glob.glob('C:\\Users\\jjh99\\PycharmProjects\\pcb\\pcb_image\\*.json')
save_json_path = 'C:\\Users\\jjh99\\PycharmProjects\\pcb\\coco_format_final.json'
labelme_to_coco(labelme_jsons, save_json_path)
