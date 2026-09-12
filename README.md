# Automatic Vehicle Registration Lookup
![ALPR Application](img-alpr.png)
## About the project

A Python-based desktop application inspired by **Automatic License Plate
Recognition (ALPR)** systems. The project detects Danish license plates
from live camera feeds or video files, extracts the plate text using
OCR, retrieves vehicle information through an API, and stores the
results in a local database.

The system combines **computer vision, deep learning, OCR, API
integration, databases, and GUI development**.

### Technologies

-   **Python**
-   **OpenCV** for video and image processing
-   **YOLO** for license plate object detection
-   **EasyOCR** for optical character recognition
-   **Tkinter** for the desktop GUI
-   **SQLite** for persistent data storage
-   **REST API / MotorAPI** for vehicle information lookup
-   **Regex** for Danish license plate format validation
-   **Multithreading** for responsive real-time processing

The application follows a **3-layer architecture** with elements of the
**MVC pattern**. The main processing pipeline is:

`Video frame → YOLO detection → license plate crop → OCR → format validation → duplicate check → API lookup → SQLite → GUI`

The project was developed iteratively and tested using both video files
and live camera input under different lighting conditions, distances,
and image qualities.

## Academic context

This was a **Programming B project completed during 3.G of the Danish
HTX (Higher Technical Examination Programme)**.

**Grade: 12**

The project was developed as part of the Programming B application
project, with a focus on applying software engineering concepts and
integrating multiple technologies into a functioning application.

## Language disclaimer

**Please note:** The project documentation and accompanying materials
are written in **Danish**, as the project was completed as part of the
Danish HTX education system.

This README provides a short English overview for readers who do not
speak Danish.

## Repository

The source code and project files are available in this repository:

`https://github.com/KhizarIrshadChaudhry/auto-vehicle-registration-lookup`

## Project documentation

The included documentation describes the application's requirements,
architecture, computational thinking, development process,
implementation, testing, and technical limitations. It also documents
the main processing workflow and the responsibilities of the individual
software components.
Document can be found at:
`Automatic Vehicle Registration System DOCS.pdf`
