import cv2
import threading
import time

class CaptureStream:
    def __init__(self):
        self.cap = None
        self.running = False
        self.frame = None
        self.lock = threading.Lock()
        self.source_info = "None"
        self.is_video_file = False

    def start_camera(self, camera_index=0):
        self.stop()
        self.cap = cv2.VideoCapture(camera_index)
        self.source_info = f"Camera {camera_index}"
        self.is_video_file = False
        self._start_thread()

    def start_video(self, file_path):
        self.stop()
        self.cap = cv2.VideoCapture(file_path)
        self.source_info = f"File: {file_path}"
        self.is_video_file = True
        self._start_thread()

    def _start_thread(self):
        if self.cap and self.cap.isOpened():
            self.running = True
            threading.Thread(target=self._capture_loop, daemon=True).start()

    def _capture_loop(self):
        while self.running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
                
                # Hvis læses fra fil, så throttle hastigheden lidt for at matche realistiske FPS
                if self.is_video_file:
                    time.sleep(0.03)
            else:
                # Slut af video eller error
                if self.is_video_file:
                    self.running = False # Stop ved sltuningen af videon
                else:
                    pass # Kamera error handling

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        time.sleep(0.1) # Tillad thread til at afslutte
        if self.cap:
            self.cap.release()
            self.cap = None
        self.frame = None