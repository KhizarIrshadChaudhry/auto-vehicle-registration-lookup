import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import cv2
import queue
from app.camera.capture_stream import CaptureStream
from app.services.processing_worker import ProcessingWorker
from app.config import settings


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatisk Nummerplade Registrering")
        self.root.geometry("1100x700")

        # Systemtilstand
        self.capture = CaptureStream()
        # Større kø til at buffer frames mellem tråde
        self.result_queue = queue.Queue(maxsize=10) 
        self.worker = ProcessingWorker(self.result_queue)
        
        # Start AI worker
        self.worker.start()

        # UI variabler
        self.input_mode = tk.StringVar(value="camera")
        self.camera_index = tk.IntVar(value=settings.DEFAULT_CAMERA_INDEX )
        self.video_path = tk.StringVar(value=settings.DEFAULT_TEST_VIDEO)
        self.status_msg = tk.StringVar(value="Klar")

        self._setup_ui()
        self._start_ui_loops()

    # _setup_ui, toggle_inputs, browse_video, start_stream, stop_stream forbliver uændrede]
    def _setup_ui(self):
        # Top Kontroller
        control_frame = tk.Frame(self.root, pady=10, bg="#e1e1e1")
        control_frame.pack(fill="x")
        tk.Label(control_frame, text="Inputkilde:", bg="#e1e1e1").pack(side="left", padx=5)
        tk.Radiobutton(control_frame, text="Kamera", variable=self.input_mode, value="camera", command=self.toggle_inputs, bg="#e1e1e1").pack(side="left")
        tk.Label(control_frame, text="Indeks:", bg="#e1e1e1").pack(side="left")
        tk.Entry(control_frame, textvariable=self.camera_index, width=3).pack(side="left", padx=5)
        tk.Radiobutton(control_frame, text="Videofil", variable=self.input_mode, value="video", command=self.toggle_inputs, bg="#e1e1e1").pack(side="left", padx=10)
        self.btn_browse = tk.Button(control_frame, text="Gennemse...", command=self.browse_video, state="disabled")
        self.btn_browse.pack(side="left")
        tk.Label(control_frame, textvariable=self.video_path, width=20, bg="#e1e1e1").pack(side="left", padx=5)
        tk.Button(control_frame, text="START", bg="green", fg="white", command=self.start_stream).pack(side="left", padx=20)
        tk.Button(control_frame, text="STOP", bg="red", fg="white", command=self.stop_stream).pack(side="left")

        # Hovedindhold
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Venstre: Video
        self.video_label = tk.Label(content_frame, text="[Ingen videofeed]", bg="black", fg="white", width=settings.PREVIEW_SIZE[0], height=settings.PREVIEW_SIZE[1])
        self.video_label.pack(side="left", anchor="n")
        # Højre: Resultater
        data_panel = tk.Frame(content_frame, width=300)
        data_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        tk.Label(data_panel, text="Seneste detektion", font=("Arial", 14, "bold")).pack(anchor="w")
        self.lbl_plate = tk.Label(data_panel, text="---", font=("Courier", 30, "bold"), fg="darkblue")
        self.lbl_plate.pack(pady=10)
        self.txt_details = tk.Text(data_panel, height=8, width=40)
        self.txt_details.pack()
        tk.Label(data_panel, text="Seneste logs:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,0))
        self.tree_log = ttk.Treeview(data_panel, columns=("Nummerplade", "Tid"), show="headings", height=10)
        self.tree_log.heading("Nummerplade", text="Nummerplade")
        self.tree_log.heading("Tid", text="Tid")
        self.tree_log.column("Nummerplade", width=100)
        self.tree_log.pack(fill="x")
        # Statuslinje
        tk.Label(self.root, textvariable=self.status_msg, bd=1, relief=tk.SUNKEN, anchor="w").pack(side="bottom", fill="x")

    def toggle_inputs(self):
        mode = self.input_mode.get()
        if mode == "video": self.btn_browse.config(state="normal")
        else: self.btn_browse.config(state="disabled")

    def browse_video(self):
        filename = filedialog.askopenfilename(filetypes=[("Videofiler", "*.mp4 *.avi *.mov")])
        if filename: self.video_path.set(filename)

    def start_stream(self):
        mode = self.input_mode.get()
        if mode == "camera":
            idx = self.camera_index.get()
            self.capture.start_camera(idx)
            self.status_msg.set(f"Startede kamera {idx}")
        else:
            path = self.video_path.get()
            if not path:
                self.status_msg.set("Fejl: Ingen videofil valgt")
                return
            self.capture.start_video(path)
            self.status_msg.set(f"Afspiller {path}")

    def stop_stream(self):
        self.capture.stop()
        self.status_msg.set("Stoppet")

    # UI-LOOP LOGIK 

    def _start_ui_loops(self):
        # Start to separate loops
        self._feed_worker()  # Loop 1: Send rå frames til worker
        self._check_queue()  # Loop 2: Modtag behandlede frames fra worker

    def _feed_worker(self):
        """Henter løbende nye frames og sender dem til worker tråden."""
        frame = self.capture.get_frame()
        if frame is not None:
            # Send til worker for behandling
            self.worker.update_frame(frame.copy(), self.capture.source_info)
        
        # Kør hurtigt for at holde worker forsynet
        self.root.after(20, self._feed_worker)

    def _check_queue(self):
        """Hoved UI opdateringsloop. Tjekker køen for behandlede frames og data."""
        try:
            # Behandl alle tilgængelige beskeder for at reducere visningslag
            while True:
                data = self.result_queue.get_nowait()
                
                if data["type"] == "frame_update":
                    self._update_video_display(data["frame"])
                elif data["type"] == "detection":
                    self._update_data_display(data)
                    
        except queue.Empty:
            pass
        finally:
            # Tjek igen ofte (30 FPS mål for UI opdatering)
            self.root.after(30, self._check_queue)

    def _update_video_display(self, frame):
        """Opdaterer videolabelen med den annoterede frame."""
        # Skaler til UI
        frame = cv2.resize(frame, settings.PREVIEW_SIZE)
        # Konverter BGR til RGB til Tkinter-visning
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        self.video_label.configure(image=img)
        # Behold reference for at undgå garbage collection
        self.video_label.image = img

    def _update_data_display(self, data):
        plate = data["plate"]
        vehicle = data["vehicle"]
        
        # Stor label
        self.lbl_plate.config(text=plate)
        
        # Detaljeboks
        info = (
            f"Type: {vehicle.get('type', 'Unknown')}\n"
            f"Status: {vehicle.get('status', 'Unknown')}\n"
            f"Første registrering: {vehicle.get('first_registration', 'Unknown')}\n"
            f"Næste syn: {vehicle.get('next_syn', 'Unknown')}\n"
            f"Mærke: {vehicle.get('make', 'Unknown')}\n"
            f"Model: {vehicle.get('model', 'Unknown')}\n"
            f"Farve: {vehicle.get('color', 'Unknown')}\n"
            f"Brændstoftype: {vehicle.get('fuel_type', 'Unknown')}"
        )
        self.txt_details.delete(1.0, tk.END)
        self.txt_details.insert(tk.END, info)
        
        # Logtabel
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        # Indsæt øverst
        self.tree_log.insert("", 0, values=(plate, ts))

    def on_close(self):
        self.capture.stop()
        self.worker.stop()
        self.root.destroy()
