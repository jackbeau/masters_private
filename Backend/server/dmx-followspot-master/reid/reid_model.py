import os
import cv2
import torch
import logging
import numpy as np
import torchvision.transforms as transforms
from torchreid.models import build_model

logger = logging.getLogger(__name__)

# Preprocessing for ReID
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

reid_model = build_model(name='osnet_x1_0', num_classes=1000, pretrained=True)
reid_model.eval()

def extract_reid_features(image):
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        features = reid_model(image).numpy().flatten()
    logger.debug(f"Extracted ReID features of length {len(features)}")
    return features

def load_database(folder):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    database = {}
    for user_folder in os.listdir(folder):
        user_path = os.path.join(folder, user_folder)
        if os.path.isdir(user_path):
            user_descriptors = []
            for img_name in os.listdir(user_path):
                img_path = os.path.join(user_path, img_name)
                img = cv2.imread(img_path)
                if img is None:
                    continue
                descriptors = extract_reid_features(img)
                if descriptors is not None:
                    user_descriptors.append(descriptors)
            if user_descriptors:
                database[user_folder] = user_descriptors
    logger.info(f"Loaded database with {len(database)} users from {folder}")
    return database

def match_descriptors(descriptors, database, threshold=10):
    best_match_id = None
    best_score = float('inf')
    for user_id, user_descriptors in database.items():
        for user_desc in user_descriptors:
            distance = np.linalg.norm(descriptors - user_desc)
            if distance < best_score:
                best_score = distance
                best_match_id = user_id
    if best_score < threshold:
        logger.debug(f"Best match: {best_match_id} with score {best_score}")
        return best_match_id, best_score
    else:
        logger.debug(f"No match found within threshold. Best score: {best_score}")
        return None, best_score
