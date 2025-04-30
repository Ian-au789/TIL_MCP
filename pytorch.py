import os
import cv2
import torch
import yaml
import random
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from glob import glob
from ultralytics import YOLO
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

# 설정
IMG_SIZE  = 1080
MIN_AREA  = 32  # 정규화된 bbox 면적 기준
SEED      = 42
TRAIN_IMG = "/kaggle/input/pothole-detection-challenge/train/images"
TRAIN_LBL = "/kaggle/input/pothole-detection-challenge/train/labels"

# 1) 전처리 결과를 저장할 디렉터리
FILTERED_DIR = "/kaggle/working/train_filtered"
IMG_SUB = os.path.join(FILTERED_DIR, "images")
LBL_SUB = os.path.join(FILTERED_DIR, "labels")
os.makedirs(IMG_SUB, exist_ok=True)
os.makedirs(LBL_SUB, exist_ok=True)

# 2) 필터링 + 링크 생성
filtered_imgs = []
for img_path in sorted(glob(os.path.join(TRAIN_IMG, "*.jpg"))):
    lbl_path = os.path.join(TRAIN_LBL, os.path.basename(img_path).replace(".jpg", ".txt"))
    if not os.path.exists(lbl_path):
        continue

    valid = False
    for line in open(lbl_path):
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        try:
            _, cx, cy, bw, bh = map(float, parts)
        except:
            continue
        if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 <= bw <= 1 and 0 <= bh <= 1):
            continue
        if bw * bh * IMG_SIZE * IMG_SIZE < MIN_AREA:
            continue
        valid = True
        break

    if not valid:
        continue

    dst_img = os.path.join(IMG_SUB, os.path.basename(img_path))
    dst_lbl = os.path.join(LBL_SUB, os.path.basename(lbl_path))
    if not os.path.exists(dst_img):
        os.symlink(img_path, dst_img)
    if os.path.exists(lbl_path) and not os.path.exists(dst_lbl):
        os.symlink(lbl_path, dst_lbl)

    filtered_imgs.append(dst_img)

print(f"✔️ 전처리 완료: {len(filtered_imgs)}개 유효 이미지")

# 3) 2400 train / 600 val 샘플링
random.seed(SEED)
train_samples = random.sample(filtered_imgs, 2400)
val_samples   = random.sample([f for f in filtered_imgs if f not in train_samples], 600)

# 4) 실험용 경로에 링크 생성
EXP_DIR   = "/kaggle/working/pothole_exp_2400_600"
TR_IMG    = os.path.join(EXP_DIR, "train/images")
TR_LBL    = os.path.join(EXP_DIR, "train/labels")
VL_IMG    = os.path.join(EXP_DIR, "valid/images")
VL_LBL    = os.path.join(EXP_DIR, "valid/labels")
os.makedirs(TR_IMG, exist_ok=True)
os.makedirs(TR_LBL, exist_ok=True)
os.makedirs(VL_IMG, exist_ok=True)
os.makedirs(VL_LBL, exist_ok=True)

def link_sample(img_list, dst_img_dir, dst_lbl_dir):
    for p in img_list:
        name = os.path.basename(p)
        lbl  = name.replace(".jpg", ".txt")
        src_lbl = os.path.join(LBL_SUB, lbl)
        dst_img = os.path.join(dst_img_dir, name)
        dst_lbl = os.path.join(dst_lbl_dir, lbl)
        if not os.path.exists(dst_img):
            os.symlink(p, dst_img)
        if os.path.exists(src_lbl) and not os.path.exists(dst_lbl):
            os.symlink(src_lbl, dst_lbl)

link_sample(train_samples, TR_IMG, TR_LBL)
link_sample(val_samples,   VL_IMG, VL_LBL)

print(f"✅ 샘플링 완료: train={len(train_samples)} / val={len(val_samples)}")

# 5) data.yaml 생성
yaml_path = os.path.join(EXP_DIR, "data.yaml")
with open(yaml_path, "w") as f:
    yaml.dump({
        'train': TR_IMG,
        'val':   VL_IMG,
        'nc': 1,
        'names': ['pothole']
    }, f)

# 6) YOLO 학습 실행
model = YOLO("yolov8s.pt")
results = model.train(
    data     = yaml_path,
    epochs   = 30,
    imgsz    = IMG_SIZE,
    batch    = 8,
    workers  = 4,
    device   = "0",
    project  = "/kaggle/working",
    name     = "filtered_2400_600",
    verbose  = True,
    show     = True,
    patience = 5,
)
