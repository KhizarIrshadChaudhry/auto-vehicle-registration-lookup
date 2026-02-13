from ultralytics import YOLO
import cv2
import numpy as np

class PlateDetector:
    def __init__(self, model_path):
        # Load model once
        self.model = YOLO(model_path)
    
    def detect(self, frame):
        """
        Returnerer en liste af bounding boxes: (x1, y1, x2, y2, confidence)
        """
        results = self.model(frame, verbose=False)
        detections = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = float(box.conf[0])
                # xyxy coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append((x1, y1, x2, y2, conf))
        
        return detections