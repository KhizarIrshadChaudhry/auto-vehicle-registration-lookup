# Software Engineering Description
# Vehicle Registration Number Registerer (MVP)


## 1. Project Overview

The **Vehicle Registration Number Registerer** is a desktop-based computer vision application built in **Python**, using **OpenCV** for image processing and **Tkinter** for the graphical user interface.

The application captures live video from a camera **or plays a user-selected video file**, detects vehicle license plates using a **YOLO-based object detection model**, extracts and recognizes the registration number using OCR, validates and deduplicates detected plates, stores results in a database, queries an external vehicle information API, and presents the results in real time within the UI.

The system is designed to be:

* Modular
* Responsive (non-blocking UI)
* Extensible (future ML models, APIs, databases)
* Suitable for real-world ALPR use cases

---

## 2. Goals & Scope (MVP)

### Primary Goals

* Real-time license plate detection from live camera feed
* Video-file based license plate detection from a local file
* OCR-based extraction of registration numbers
* Deduplication of repeated plate detections
* Storage of plate events in a database
* API lookup of vehicle details by registration number
* Responsive Tkinter-based UI
* UI selection of input source (camera index or video file)

### Out of Scope (for MVP)

* Multi-camera simultaneous processing
* User authentication
* Cloud synchronization
* Model training pipeline (pretrained YOLO only)
* Web-based UI

---

## 3. Functional Requirements

### FR-1 Camera Capture

* The system shall capture live video using OpenCV.
* The capture process shall run in a background thread.
* The UI shall always remain responsive.

### FR-1B Video File Input Selection (NEW)

* The system shall allow the user to choose a video file (e.g., `.mp4`, `.mov`, `.avi`) from within the Tkinter UI.
* When a video file is selected, the system shall use it as the input stream instead of a camera.
* The system shall support switching between camera and video input without restarting the application.

### FR-1C Camera Selection (NEW)

* The system shall allow the user to select a camera input index from within the Tkinter UI (e.g., 0, 1, 2).
* The selected camera index shall be used when starting the camera stream.

---

### FR-2 Live Preview

* The live camera feed shall be displayed in a Tkinter window.
* Frames shall be resized to fit the preview area.

### FR-2B Video Playback Preview (NEW)

* When video input is selected, the preview shall display video frames sequentially.
* When the video reaches the end, the system shall stop playback automatically or optionally loop playback.
* The UI shall display a status message such as **"Video finished"**.

---

### FR-3 License Plate Detection

* The system shall use a pretrained YOLO object detection model to detect license plates.
* Detection shall return bounding boxes with confidence scores.

### FR-4 Plate Cropping

* Detected bounding boxes shall be used to crop plate regions from the frame.

### FR-5 OCR Recognition

* The system shall extract text from cropped plate images using OCR.
* OCR output shall include recognized text and confidence score.

### FR-6 Text Normalization & Validation

* OCR output shall be normalized (uppercase, remove whitespace/symbols).
* Registration numbers shall be validated against country-specific patterns.
* Invalid plates shall be discarded.

### FR-7 Deduplication

* The system shall prevent repeated storage of the same plate within a configurable cooldown period.
* A plate must be detected consistently or with sufficient confidence before confirmation.

### FR-8 Database Storage

* Each confirmed plate detection shall be stored with:

  * Plate number
  * Timestamp
  * Confidence
  * Input source metadata (camera index or video file path)
  * Optional image path
* Vehicle details shall be stored separately and linked to plate events.

### FR-9 Vehicle API Integration

* The system shall query an external vehicle information API using the plate number.
* API calls shall run asynchronously.

### FR-10 UI Feedback

* The UI shall display:

  * Live camera feed / video playback
  * Current status
  * Recently detected plates
  * Vehicle details
  * Current input source
* Errors and warnings shall be visible to the user.

---

## 4. Non-Functional Requirements

### Performance

* UI refresh rate ≥ 20 FPS (subject to hardware)
* Detection loop decoupled from UI thread
* Video playback optionally throttled to video FPS

### Reliability

* Camera and video file errors handled gracefully
* API failures logged without crashing the application

### Maintainability

* Clear module boundaries
* No OpenCV logic inside UI code

### Portability

* Runs on macOS, Windows, Linux (Python 3.12+)

---

## 5. System Architecture

### High-Level Architecture

```
Input Source (Camera or Video)
        ↓
   CameraStream / VideoStream
        ↓
    Frame Buffer (latest frame)
        ↓
Plate Detection (YOLO)
        ↓
OCR + Normalize + Validate
        ↓
Tracker (Dedup + Confirmation)
        ↓
Database + API Worker
        ↓
UI (Preview + Results)
```

### Threading Model

* Main Thread: Tkinter UI
* Capture Thread: OpenCV stream reader (camera or video)
* Processing Threads: YOLO + OCR
* Worker Thread: API calls + DB writes

Communication via `queue.Queue` and `root.after()` polling.

---

## 6. Project Structure (Template)

```
auto-vehicle-registration-lookup/
├── app/
│   ├── main.py
│   ├── ui/
│   │   ├── main_window.py
│   │   └── widgets.py
│   ├── camera/
│   │   ├── camera_stream.py
│   │   └── video_stream.py
│   ├── vision/
│   │   ├── plate_detector.py
│   │   ├── ocr_reader.py
│   │   ├── preprocess.py
│   │   └── tracker.py
│   ├── services/
│   │   ├── database.py
│   │   ├── vehicle_api.py
│   │   └── job_queue.py
│   ├── models/
│   │   └── types.py
│   └── config/
│       └── settings.py
├── data/
│   ├── snapshots/
│   └── db/
├── tests/
└── requirements.txt
```

---

## 7. Module Responsibilities (Updated)

### camera/camera_stream.py

* Camera capture using OpenCV
* Thread-safe frame access

### camera/video_stream.py

* Video file playback using OpenCV
* EOF detection and optional looping

### ui/main_window.py

* Source selection (Camera / Video)
* Camera index selection
* Video file chooser dialog
* Preview display and controls

---

## 8. UI Requirements (Detailed)

* Video preview area
* Source selector (radio buttons)
* Camera index selector
* Video file chooser button
* Start / Stop / Snapshot / Quit buttons
* Status label
* Recent detections list
* Vehicle details panel

---

## 9. Data Storage Updates

`plate_events` table must include:

* `input_type`: `camera` or `video`
* `input_ref`: `camera:1` or `video:/path/to/file.mp4`

---

## 10. File Templates (MVP Skeleton)

* `camera_stream.py`: Camera capture abstraction
* `video_stream.py`: Video playback abstraction
* `main_window.py`: UI logic and source selection
* `job_queue.py`: Background processing

---

## 11. MVP Completion Criteria

The MVP is complete when:

* User can select camera or video input
* Camera preview and video playback both function
* YOLO-based plate detection works
* OCR extracts valid plate numbers
* Duplicate detections are avoided
* Plates and vehicle data are stored
* UI remains responsive at all times

---