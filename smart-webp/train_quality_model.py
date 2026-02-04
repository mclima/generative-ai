# train_quality_model.py
# pip install pillow scikit-image xgboost numpy pandas joblib opencv-python
# python3 train_quality_model.py

import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from skimage.filters import sobel
from skimage.color import rgb2gray
from xgboost import XGBRegressor
import joblib

# -------------------------------
# CONFIGURATION
# -------------------------------
IMAGES_DIR = "data/images"        # folder with your JPG/PNG images
LABELS_FILE = "data/labels.csv"   # CSV: filename,quality
MODEL_OUTPUT = "model.pkl"

# -------------------------------
# FEATURE FUNCTIONS
# -------------------------------

def is_png(filename):
    return int(filename.lower().endswith(".png"))

def entropy(img_gray):
    """Compute Shannon entropy of grayscale image"""
    hist, _ = np.histogram(img_gray, bins=256, range=(0, 255))
    hist = hist[hist > 0] / img_gray.size
    return -np.sum(hist * np.log2(hist))

def edge_density(img_gray):
    """Compute edge density using Sobel filter"""
    edges = sobel(img_gray)
    return np.mean(edges)

def extract_features(image_path):
    """Return feature vector for a single image"""
    ext_flag = is_png(image_path)
    img = Image.open(image_path).convert("RGB")
    img_gray = np.array(rgb2gray(np.array(img)) * 255).astype(np.uint8)
    ent = entropy(img_gray)
    edges = edge_density(img_gray)
    return [ext_flag, ent, edges]

# -------------------------------
# LOAD LABELS
# -------------------------------
labels_df = pd.read_csv(LABELS_FILE)
features = []
targets = []

for idx, row in labels_df.iterrows():
    img_file = os.path.join(IMAGES_DIR, row['filename'])
    if not os.path.exists(img_file):
        print(f"Warning: {img_file} not found, skipping")
        continue
    feats = extract_features(img_file)
    features.append(feats)
    targets.append(row['quality'])

X = np.array(features)
y = np.array(targets)

# -------------------------------
# TRAIN MODEL
# -------------------------------
model = XGBRegressor(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    objective="reg:squarederror",
    random_state=42
)
model.fit(X, y)

# -------------------------------
# SAVE MODEL
# -------------------------------
joblib.dump(model, MODEL_OUTPUT)
print(f"Model saved to {MODEL_OUTPUT}")
