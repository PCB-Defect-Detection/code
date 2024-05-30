import json
import cv2
import os
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2.data import MetadataCatalog
from detectron2.data.datasets import register_coco_instances
from detectron2 import model_zoo

# 데이터셋 경로 설정
base_dir = "C:\\Users\\jjh99\\PycharmProjects\\pcb"
coco_json = os.path.join(base_dir, "coco_format_1.json")
image_dir = os.path.join(base_dir, "pcb_image")

# COCO JSON 파일에서 카테고리 이름 읽기
with open(coco_json) as f:
    coco_data = json.load(f)
categories = [category['name'] for category in coco_data['categories']]

# 데이터셋 등록
register_coco_instances("my_dataset", {}, coco_json, image_dir)

# Metadata 설정
MetadataCatalog.get("my_dataset").thing_classes = categories

# Config 설정
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.75  # Threshold
cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")  # 훈련된 모델 가중치 경로
cfg.MODEL.DEVICE = "cuda"  # 'cpu' 또는 'cuda'
cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(categories)  # 실제 클래스 수로 조정

# 예측기 설정
predictor = DefaultPredictor(cfg)

# 웹캠 인덱스 설정
cam_index = 1
cap = cv2.VideoCapture(cam_index)
if not cap.isOpened():
    print(f"Error: Could not open webcam {cam_index}.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # 예측 수행
    outputs = predictor(frame)

    # 예측 결과 시각화
    v = Visualizer(frame[:, :, ::-1],
                   metadata=MetadataCatalog.get("my_dataset"),
                   scale=0.8,
                   instance_mode=ColorMode.IMAGE
                   )
    v = v.draw_instance_predictions(outputs["instances"].to("cpu"))

    # 시각화된 프레임을 화면에 표시
    cv2.imshow('Predictions', v.get_image()[:, :, ::-1])

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 캡처 해제 및 모든 창 닫기
cap.release()
cv2.destroyAllWindows()
