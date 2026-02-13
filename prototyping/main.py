#usind python 3.12.10
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import time

import ssl
import cv2
from ultralytics import YOLO
import easyocr


class TkCamApp:
    def __init__(self, root, camera_index="video.mp4", model_path='license_plate_detector.pt'):
        self.root = root
        self.root.title("Tkinter Camera Preview (OpenCV)")




        # window size
        self.preview_w = 960
        self.preview_h = 540

        self.video_label = tk.Label(
            root,
            width=self.preview_w,
            height=self.preview_h,
            bg="black"
        )
        self.video_label.pack(padx=10, pady=10)

        controls = tk.Frame(root)
        controls.pack(pady=(0, 8))

        tk.Button(controls, text="Start", command=self.start).pack(side="left", padx=5)
        tk.Button(controls, text="Stop", command=self.stop).pack(side="left", padx=5)
        tk.Button(controls, text="Snapshot", command=self.snapshot).pack(side="left", padx=5)
        tk.Button(controls, text="Quit", command=self.on_close).pack(side="left", padx=5)

        self.status = tk.StringVar(value="Idle")
        tk.Label(root, textvariable=self.status).pack()

        self.camera_index = camera_index
        self.cap = None
        self.running = False

        self.frame_bgr = None  # single shared frame
        self.thread = None

        ssl._create_default_https_context = ssl._create_stdlib_context

        self.model_path = model_path
        self.model = YOLO(self.model_path)
        self.reader = easyocr.Reader(['en']) # OCR



        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start UI updater asap
        self.update_ui()

        # Auto start camera
        self.root.after(200, self.start)

    def start(self):
        if self.running:
            return

        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_AVFOUNDATION)
        if not self.cap.isOpened():
            self.status.set("Could not open camera")
            return

        self.running = True
        self.status.set("Camera running")

        self.thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.status.set("Stopped")

        if self.cap:
            self.cap.release()
            self.cap = None

    def capture_loop(self):
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

    
    

    def update_ui(self):
        """Main thread: display latest frame"""
        if self.frame_bgr is not None:
            frame_rgb = cv2.cvtColor(self.frame_bgr, cv2.COLOR_BGR2RGB)

            # Resize to fit label
            frame_rgb = cv2.resize(
                frame_rgb,
                (self.preview_w, self.preview_h),
                interpolation=cv2.INTER_AREA
            )

            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(img)

            # keep reference
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Always reschedule also even if no frame yet
        self.root.after(20, self.update_ui)

    def snapshot(self):
        if self.frame_bgr is None:
            self.status.set("No frame yet")
            return
        name = f"snapshot_{int(time.time())}.png"
        cv2.imwrite(name, self.frame_bgr)
        self.status.set(f"Pic Saved {name}")



    def on_close(self):
        self.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TkCamApp(root)
    root.mainloop()
