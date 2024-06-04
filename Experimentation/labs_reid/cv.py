import os
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import uuid
import torch
import torchvision.transforms as transforms
from torchreid.models import build_model
from collections import defaultdict, deque

# Load YOLO model
model = YOLO("yolov8n-seg.pt")  # Adjust to your specific YOLO model

# Define paths
USER_FOLDER = 'users'
UNCERTAIN_FOLDER = 'uncertain'

# Create folders if they don't exist
os.makedirs(USER_FOLDER, exist_ok=True)
os.makedirs(UNCERTAIN_FOLDER, exist_ok=True)

# Initialize the ReID model using Torchreid
reid_model = build_model(name='osnet_x1_0', num_classes=1000, pretrained=True)
reid_model.eval()

# Preprocessing for ReID
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Function to extract ReID features from an image
def extract_reid_features(image):
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        features = reid_model(image).numpy().flatten()
    return features

# Function to load database descriptors from images or a file
def load_database(folder):
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
    return database

database = load_database(USER_FOLDER)
uncertain_database = load_database(UNCERTAIN_FOLDER)

# Unified function to match ReID descriptors
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
        return best_match_id, best_score
    else:
        return None, best_score

def seg_to_bbox(mask):
    x_coords, y_coords = mask[:, 0], mask[:, 1]
    return np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords)

# Initialize webcam
cap = cv2.VideoCapture(3)  # Use 0 for webcam

# Periodic saving settings
save_interval = 30  # Save an image every 30 frames
frame_count = 0 

# Mapping of YOLO IDs to user folders
yolo_id_to_user = {}
track_histories = defaultdict(lambda: deque(maxlen=10))  # Maintain a history of the last 10 IDs for each track

# Colors for consistent annotation
user_colors = {}

while True:
    ret, im0 = cap.read()
    if not ret:
        print("Video feed is empty, no frame found.")
        break

    # Initialize annotator
    annotator = Annotator(im0.copy(), line_width=2)

    # Perform detection and tracking with YOLOv8
    results = model.track(source=im0, persist=True)  # Use appropriate tracker

    # Process detections
    if results[0].boxes.id is not None and results[0].masks is not None:
        masks = results[0].masks.xy
        track_ids = results[0].boxes.id.int().cpu().tolist()

        for mask, track_id in zip(masks, track_ids):
            # Convert mask to bbox
            x1, y1, x2, y2 = seg_to_bbox(mask)
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # Check if bounding box outside of image
            if x1 < 0 or y1 < 0 or x2 >= im0.shape[1] or y2 >= im0.shape[0]:
                continue
            person_image = im0[y1:y2, x1:x2]

            # Check if person_image is empty
            if person_image.size == 0:
                continue

            # Extract ReID features
            descriptors = extract_reid_features(person_image)
            label = f'ID: {track_id} - Not Identified'

            if descriptors is not None and descriptors.size > 0:
                # Always check against the certain database first
                match_id, score = match_descriptors(descriptors, database, threshold=15)

                if match_id:  # If a valid match is found in the user database
                    user_folder = os.path.join(USER_FOLDER, match_id)
                    os.makedirs(user_folder, exist_ok=True)

                    if frame_count % save_interval == 0:
                        img_name = f'{uuid.uuid4()}.jpg'
                        img_path = os.path.join(user_folder, img_name)
                        cv2.imwrite(img_path, person_image)

                    track_histories[track_id].append((match_id, score))
                else:
                    # Check against the uncertain database
                    uncertain_match_id, uncertain_score = match_descriptors(descriptors, uncertain_database, threshold=20)

                    if uncertain_match_id:  # If a valid match is found in the uncertain database
                        uncertain_user_folder = os.path.join(UNCERTAIN_FOLDER, uncertain_match_id)
                        os.makedirs(uncertain_user_folder, exist_ok=True)
                        img_name = f'{uuid.uuid4()}.jpg'
                        img_path = os.path.join(uncertain_user_folder, img_name)
                        cv2.imwrite(img_path, person_image)

                        track_histories[track_id].append((uncertain_match_id, uncertain_score))
                    else:  # Create a new uncertain user only if no match is found in uncertain database
                        new_uncertain_id = f'uncertain_{len(os.listdir(UNCERTAIN_FOLDER))}'
                        new_uncertain_folder = os.path.join(UNCERTAIN_FOLDER, new_uncertain_id)
                        os.makedirs(new_uncertain_folder, exist_ok=True)
                        img_name = f'{uuid.uuid4()}.jpg'
                        img_path = os.path.join(new_uncertain_folder, img_name)
                        cv2.imwrite(img_path, person_image)
                        uncertain_database[new_uncertain_id] = [descriptors]

                        track_histories[track_id].append((new_uncertain_id, uncertain_score))

            # Determine the most frequent ID in the history
            if len(track_histories[track_id]) > 0:
                id_counts = defaultdict(int)
                for id, score in track_histories[track_id]:
                    id_counts[id] += 1
                best_match_id = max(id_counts, key=id_counts.get)
                match_percentage = (id_counts[best_match_id] / len(track_histories[track_id])) * 100
                best_score = min(score for id, score in track_histories[track_id] if id == best_match_id)
                label = f'ID: {track_id} - {best_match_id} ({match_percentage:.2f}%) Score: {best_score:.2f}'

                yolo_id_to_user[track_id] = best_match_id
                user_colors[best_match_id] = colors(len(user_colors), True)

            # Debug statement to check track_id and label
            print(f"Track ID: {track_id}, Label: {label}")

            annotator.box_label([x1, y1, x2, y2], label, color=user_colors.get(yolo_id_to_user.get(track_id, track_id), colors(track_id, True)))

    # Increment frame count
    frame_count += 1

    # Display the annotated frame
    im0_annotated = annotator.result()
    cv2.imshow("Real-Time Detection and Tracking", im0_annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
