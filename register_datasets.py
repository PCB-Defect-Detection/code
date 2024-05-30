from detectron2.data.datasets import register_coco_instances
import os

# 절대 경로 지정
base_dir = "C:\\Users\\jjh99\\PycharmProjects\\pcb"
coco_json = os.path.join(base_dir, "coco_format_1.json")
image_dir = os.path.join(base_dir, "pcb_image")

# 데이터셋 등록
register_coco_instances("my_dataset", {}, coco_json, image_dir)
