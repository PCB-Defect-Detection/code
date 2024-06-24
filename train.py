import os
import json
from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.data.datasets import register_coco_instances
from detectron2.data import MetadataCatalog
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.modeling import build_model
from detectron2.modeling.roi_heads import FastRCNNOutputLayers
import torch.nn as nn
import torch

# 데이터셋 경로 설정
base_dir = "C:\\Users\\jjh99\\PycharmProjects\\pcb"
coco_json = os.path.join(base_dir, "coco_format_final.json")
image_dir = os.path.join(base_dir, "pcb_image")

# 데이터셋 등록
register_coco_instances("my_dataset", {}, coco_json, image_dir)

# coco_format.json에서 카테고리 이름 가져오기
with open(coco_json) as f:
    coco_data = json.load(f)
categories = [category['name'] for category in coco_data['categories']]

# Metadata 설정
MetadataCatalog.get("my_dataset").thing_classes = categories

if __name__ == "__main__":
    # Config 설정
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))

    # 등록된 데이터셋을 TRAIN에 추가
    cfg.DATASETS.TRAIN = ("my_dataset",)
    cfg.DATASETS.TEST = ()
    cfg.DATALOADER.NUM_WORKERS = 4  # DataLoader 작업자 수
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
    cfg.SOLVER.IMS_PER_BATCH = 2
    cfg.SOLVER.BASE_LR = 0.0001  # 학습률을 더 낮춤
    cfg.SOLVER.MAX_ITER = 1000  # 훈련 반복 횟수 조절
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(categories)  # 실제 클래스 수로 조정

    # Gradient Clipping 설정
    cfg.SOLVER.CLIP_GRADIENTS.ENABLED = True
    cfg.SOLVER.CLIP_GRADIENTS.CLIP_VALUE = 1.0
    cfg.SOLVER.CLIP_GRADIENTS.CLIP_TYPE = "value"
    cfg.SOLVER.CLIP_GRADIENTS.NORM_TYPE = 2.0

    # 출력 디렉토리 설정
    cfg.OUTPUT_DIR = os.path.join(base_dir, "output")
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

    # 모델 빌드 및 가중치 로드
    model = build_model(cfg)
    DetectionCheckpointer(model).load(cfg.MODEL.WEIGHTS)  # 기존 가중치를 로드하지만, ROI 헤드는 무시

    # ROI 헤드 재구성
    input_shape = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNOutputLayers(cfg, input_shape)

    # ROI 헤드의 가중치 재설정
    def reset_cls_weights(predictor):
        nn.init.normal_(predictor.cls_score.weight, std=0.01)
        nn.init.constant_(predictor.cls_score.bias, 0)
        nn.init.normal_(predictor.bbox_pred.weight, std=0.001)
        nn.init.constant_(predictor.bbox_pred.bias, 0)

    reset_cls_weights(model.roi_heads.box_predictor)

    # 트레이너 설정 및 훈련 시작
    trainer = DefaultTrainer(cfg)
    trainer.resume_or_load(resume=False)
    trainer.train()
