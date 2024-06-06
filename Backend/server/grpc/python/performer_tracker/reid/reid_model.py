"""
Author: Jack Beaumont
Date: 06/06/2024

This module provides a PersonReID class for person re-identification using a
custom OSNet model.

The class includes methods to load the model, extract features, load a
database of descriptors, and match descriptors.
"""

import os
import cv2
import torch
import logging
import numpy as np
import torchvision.transforms as transforms
from torchreid.models import osnet_x1_0

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonReID:
    def __init__(self, model_path="models/osnet_x1_0.pth"):
        """
        Initialize the PersonReID class.

        Parameters:
        model_path (str): Path to the pretrained OSNet model.
        """
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        self.reid_model = self._load_custom_osnet_model()
        self.reid_model.eval()
        self.transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize((256, 128)),
                transforms.ToTensor(),
                transforms.Normalize(
                    [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
                ),
            ]
        )

    def _load_custom_osnet_model(self):
        """
        Load the custom OSNet model from the specified path.

        Returns:
        torch.nn.Module: Loaded OSNet model.

        Raises:
        FileNotFoundError: If the model file does not exist.
        """
        model = osnet_x1_0(pretrained=False)
        if os.path.exists(self.model_path):
            state_dict = torch.load(self.model_path, map_location="cpu")
            model.load_state_dict(state_dict)
            self.logger.debug("Model loaded successfully")
        else:
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        return model

    def extract_reid_features(self, image):
        """
        Extract re-identification features from an image.

        Parameters:
        image (np.ndarray): Input image.

        Returns:
        np.ndarray: Extracted features.
        """
        image = self.transform(image).unsqueeze(0)
        with torch.no_grad():
            features = self.reid_model(image).numpy().flatten()
        self.logger.debug(f"Extracted ReID features of length {len(features)}")
        return features

    def load_database(self, folder):
        """
        Load a database of user descriptors from a specified folder.

        Parameters:
        folder (str): Path to the folder containing user images.

        Returns:
        dict: Database of user descriptors.
        """
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
                    descriptors = self.extract_reid_features(img)
                    if descriptors is not None:
                        user_descriptors.append(descriptors)
                if user_descriptors:
                    database[user_folder] = user_descriptors
        self.logger.info(
            f"Loaded database with {len(database)} users from {folder}"
        )
        return database

    def match_descriptors(self, descriptors, database, threshold=10):
        """
        Match input descriptors against a database of descriptors.

        Parameters:
        descriptors (np.ndarray): Descriptors to match.
        database (dict): Database of user descriptors.
        threshold (float): Distance threshold for matching.

        Returns:
        tuple: Best matching user ID and score if a match is found within the
               threshold, otherwise (None, best_score).
        """
        best_match_id = None
        best_score = float("inf")
        for user_id, user_descriptors in database.items():
            for user_desc in user_descriptors:
                distance = np.linalg.norm(descriptors - user_desc)
                if distance < best_score:
                    best_score = distance
                    best_match_id = user_id
        if best_score < threshold:
            self.logger.debug(
                f"Best match: {best_match_id} with score {best_score}"
            )
            return best_match_id, best_score
        else:
            self.logger.debug(
                f"No match found within threshold. Best score: {best_score}"
            )
            return None, best_score
