import cv2
from ultralytics import YOLO
import easyocr

# Source - https://stackoverflow.com/a/77834685
# Posted by ghareeb fathy
# Retrieved 2026-02-02, License - CC BY-SA 4.0

import ssl




class ANPRDetector:
    def __init__(self, model_path='license_plate_detector.pt', cap=1):
        ssl._create_default_https_context = ssl._create_stdlib_context

        self.model_path = model_path
        self.cap = cv2.VideoCapture(cap)
        self.model = YOLO(self.model_path)
        self.reader = easyocr.Reader(['en']) # OCR

        self.detect_and_read()

    def detect_and_read(self):
        reader = easyocr.Reader(['en'])
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            results = self.model(frame)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    license_plate_crop = frame[y1:y2, x1:x2]
                    plate_text = reader.readtext(license_plate_crop, detail=0)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, str(plate_text), (x1, y1-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

            cv2.imshow('ANPR', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = ANPRDetector(cap="video.mp4")


'''
# 1. Load YOLOv8 Model
#https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8/blob/main/license_plate_detector.pt
model = YOLO('license_plate_detector.pt') # Path to your custom trained model
reader = easyocr.Reader(['en'])

# 2. Capture Video/Image
cap = cv2.VideoCapture(1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # 3. Detect Plate
    results = model(frame)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Get coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # 4. Crop and Read
            license_plate_crop = frame[y1:y2, x1:x2]
            #plate_text = reader.readtext(license_plate_crop, detail=0)
            
            # 5. Draw
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            #cv2.putText(frame, str(plate_text), (x1, y1-10), 
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

    cv2.imshow('ANPR', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
'''

