import os
from dotenv import load_dotenv

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "db", "plates.db")
SNAPSHOTS_DIR = os.path.join(DATA_DIR, "snapshots")
MODEL_PATH = os.path.join(BASE_DIR, "models/yolov8n_license_plate_detector_v1.pt")

# Vision
CONFIDENCE_THRESHOLD = 0.65
OCR_CONFIDENCE_THRESHOLD = 0.3
DEDUPLICATION_COOLDOWN = 10  # Sekunder før samme nr. plade registreres igen

# Cam/Video
DEFAULT_CAMERA_INDEX = 1 # 1 on Apple Mac
DEFAULT_TEST_VIDEO = "data/test_videos/test_driveway_daylight.mp4" # Default video til testing
PREVIEW_SIZE = (640, 360) # Cam/video preview størelse i UI


MOTER_API_KEY = os.getenv("MOTER_API_KEY")
MOTER_API_URL = "https://v1.motorapi.dk"
