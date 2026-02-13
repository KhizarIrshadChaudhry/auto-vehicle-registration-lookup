import easyocr
import re

class OCRReader:
    def __init__(self):
        # Initialize Reader
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    def read_text(self, cropped_image):
        """
        Returnere normaliseret tekst og confidence KUN hvis det matcher formatet.
        """
        try:
            result = self.reader.readtext(cropped_image, detail=1)
            
            best_text = ""
            best_conf = 0.0

            # Find detektionen med højeste confidence
            for (bbox, text, conf) in result:
                if conf > best_conf:
                    best_conf = conf
                    best_text = text
            
            if best_text:
                normalized_text = self.normalize(best_text)
                
                if self.is_valid_format(normalized_text):
                    return normalized_text, best_conf
                
            return None, 0.0
            
        except Exception as e:
            print(f"OCR Error: {e}")
            return None, 0.0

    def normalize(self, text):
        """
        Konveretere 'AB 12 345' -> 'AB12345'
        Fjernes spaces, dashes, og gør uppercase
        """
        return re.sub(r'[^A-Z0-9]', '', text.upper())

    def is_valid_format(self, text):
        """
        Til danske nummerplade: 2 Letters + 5 Digits
        """
        # Regex fra stackoverflow Start(^) + [A-Z] præcis 2 gange + [0-9] præcis 5 gange
        pattern = r'^[A-Z]{2}\d{5}$'
        
        return bool(re.match(pattern, text))