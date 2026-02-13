import time
from app.config import settings

class DetectionTracker:
    def __init__(self):
        #Dict til gemme sidste set tid: { "PLATE123": timestamp }
        self.seen_plates = {}

    def is_new_detection(self, plate_text):
        now = time.time()
        last_seen = self.seen_plates.get(plate_text)

        if last_seen is None:
            self.seen_plates[plate_text] = now
            return True
        
        if (now - last_seen) > settings.DEDUPLICATION_COOLDOWN:
            self.seen_plates[plate_text] = now
            return True
            
        return False