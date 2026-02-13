import threading
import time
import queue
import cv2
from app.vision.plate_detector import PlateDetector
from app.vision.ocr_reader import OCRReader
from app.vision.tracker import DetectionTracker
from app.services.vehicle_api import VehicleAPIService
from app.services.database import DatabaseService
from app.config import settings

class ProcessingWorker:
    def __init__(self, result_queue):
        self.result_queue = result_queue
        self.running = False
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        
        # Initialize services
        self.detector = None 
        self.ocr = None
        self.tracker = DetectionTracker()
        self.api = VehicleAPIService()
        self.db = DatabaseService()

    def update_frame(self, frame, source_name):
        with self.frame_lock:
            self.latest_frame = (frame, source_name)

    def start(self):
        self.running = True
        threading.Thread(target=self._process_loop, daemon=True).start()

    def _process_loop(self):
        print("Loading AI Models...")
        self.detector = PlateDetector(settings.MODEL_PATH)
        self.ocr = OCRReader()
        print("Models Loaded.")

        while self.running:
            input_data = None
            with self.frame_lock:
                if self.latest_frame:
                    input_data = self.latest_frame
                    # Don't clear latest_frame immediately to allow processing to catch up
                    # Clear ikke latest_frame her - skal bruges til at holde styr på om de er kommet ny frames og hurtig proces
            
            if input_data:
                frame, source_name = input_data
                self._process_frame(frame, source_name)
            else:
                time.sleep(0.01)

    def _process_frame(self, frame, source_name):
        # Create a copy for drawing annotations
        annotated_frame = frame.copy()
        
        detections = self.detector.detect(frame)
        
        for (x1, y1, x2, y2, conf) in detections:
            #print(f"Detected plate with confidence {conf:.2f} at [{x1}, {y1}, {x2}, {y2}]")
            if conf < settings.CONFIDENCE_THRESHOLD:
                continue

            # --- Draw Green Box ---
            # Color is BGR: (0, 255, 0) for green
            # Thickness is 2px
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Crop plate from original raw frame for OCR
            plate_img = frame[y1:y2, x1:x2]
            
            # OCR
            text, ocr_conf = self.ocr.read_text(plate_img)
            #print(f"OCR Result: '{text}' with confidence {ocr_conf:.2f}")
            
            if text and ocr_conf > settings.OCR_CONFIDENCE_THRESHOLD:
                # Deduplicate
                if self.tracker.is_new_detection(text):
                    # Fetch Data
                    vehicle_data = self.api.lookup_vehicle(text)
                    
                    # Save DB
                    self.db.insert_plate(text, conf, source_name, vehicle_data)
                    
                    # Send data result to UI
                    result_pack = {
                        "type": "detection",
                        "plate": text,
                        "conf": conf,
                        "vehicle": vehicle_data
                    }
                    self.result_queue.put(result_pack)

        # --- Send Annotated Frame to UI ---
        # Always send the processed frame for display, even if nothing was detected.
        frame_pack = {
            "type": "frame_update",
            "frame": annotated_frame
        }
        # Use put_nowait to avoid blocking processing thread if UI is slow
        try:
            self.result_queue.put_nowait(frame_pack)
        except queue.Full:
            pass # Drop frame if UI is falling behind

    def stop(self):
        self.running = False
        self.db.close()
