#using python 3.12.10
#THIS CODE DEMONSTRATES THE USE OF OPENCV INSIDE OF TKINTER
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import time


class TkCamApp:
    def __init__(self, root, camera_index=1):
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
        """Background thread: capture frames"""
        while self.running and self.cap:
            ok, frame = self.cap.read()
            if ok and frame is not None:
                self.frame_bgr = frame
            time.sleep(0.01)

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
    app = TkCamApp(root, camera_index=1)
    root.mainloop()
