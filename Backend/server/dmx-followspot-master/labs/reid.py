import torch
import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort
from torchreid.utils import FeatureExtractor
from PIL import Image
import numpy as np

# Initialize YOLO model
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Initialize the FeatureExtractor
extractor = FeatureExtractor(
    model_name='osnet_x1_0',
    model_path='',  # If you have a specific model path, provide it here
    device='cuda' if torch.cuda.is_available() else 'cpu'
)

# Initialize the DeepSort tracker
tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0)

# Function to process each frame
def process_frame(frame):
    # Detect objects with YOLO
    results = yolo_model(frame)
    detections = []

    for det in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = det
        if int(cls) == 0:  # Filter for person class (class 0)
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            crop_img = frame[y1:y2, x1:x2]
            crop_img_rgb = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)  # Convert to RGB
            features = extractor(crop_img_rgb)
            detections.append([x1, y1, x2-x1, y2-y1, conf.item(), features.cpu().numpy().flatten()])  # Ensure conf is a float and features are numpy array

    print("Detections:", detections)  # Debug statement
    
    # Draw bounding boxes for detections
    for det in detections:
        x1, y1, width, height, conf, _ = det
        x2 = x1 + width
        y2 = y1 + height
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'ID: {int(conf*100)}%', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)


    # try:
    #     # Update tracker
    #     tracks = tracker.update_tracks(detections, frame)  # Get the tracks after updating

    #     # Draw tracks on the frame
    #     for track in tracks:
    #         if not track.is_confirmed() or track.time_since_update > 1:
    #             continue
    #         bbox = track.to_tlbr()
    #         track_id = track.track_id
    #         cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0), 2)
    #         cv2.putText(frame, str(track_id), (int(bbox[0]), int(bbox[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)

    # except Exception as e:
    #     print(f"Error updating tracks: {e}")

    return frame

# Main function to process the video
def main():
    cap = cv2.VideoCapture(3)  # Use video device 3
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = process_frame(frame)
        cv2.imshow('Frame', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
