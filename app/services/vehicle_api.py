import time
import random

import requests
from app.config import settings

class VehicleAPIService:
    """
    Service til look up bil information vha. bil nummerplade gennem MoterAPI
     - https://moterapi.dk/docs/overview
     - Endpoints: GET /vehicles/{plate_number}
    """

    def __init__(self):
        self.base_url = settings.MOTER_API_URL
        self.api_key = settings.MOTER_API_KEY

        if not self.api_key:
            print("WARNING: MOTER_API_KEY not found in .env.")

        
    def lookup_vehicle(self, plate_number):
        """
        Bruger MoterAPI med endtpoint GET /vehicles?{nummerpalde}
        """

        clean_plate = plate_number.replace(" ", "").upper()

        url = f"{self.base_url}/vehicles/{clean_plate}"
        headers = {
            "X-AUTH-TOKEN": self.api_key
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                next_syn = None
                mot_info = data.get("mot_info")
                if isinstance(mot_info, dict):
                    next_syn = mot_info.get("next_inspection_date")
                if not next_syn:
                    next_syn = data.get("next_inspection_date")

                first_registration = data.get("first_registration")
                if not first_registration:
                    first_registration = data.get("first_registration_date")

                return {
                    "plate": clean_plate,
                    "type": data.get("type", "Unknown"),
                    "status": data.get("status", "Unknown"),
                    "first_registration": first_registration or "Unknown",
                    "next_syn": next_syn or "Unknown",
                    "make": data.get("make", "Unknown"),
                    "model": data.get("model", "Unknown"),
                    "color": data.get("color", "Unknown"),
                    "fuel_type": data.get("fuel_type", "Unknown"),
                }
            
            elif response.status_code == 404:
                return self._error_response(clean_plate, "Vehicle not found")
            
            elif response.status_code == 401:
                return self._error_response(clean_plate, "Unauthorized: tjek API key")
            
            else:
                return self._error_response(clean_plate, f"API error: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            print("API Request Error:", e)
            return self._error_response(clean_plate, f"Request failed: {e}")
    
    def _error_response(self, plate, message):
        return {
                    "plate": plate,
                    "type": "Unknown",
                    "status": "Unknown",
                    "first_registration": "Unknown",
                    "next_syn": "Unknown",
                    "make": "Unknown",
                    "model": "Unknown",
                    "color": "Unknown",
                    "fuel_type": "Unknown"}
            
    def mock_lookup_vehicle(self, plate_number):
        # Simulere latency
        time.sleep(0.5) 
        
        # Mock til demonstration og testing
        mock_brands = ["Toyota", "Honda", "Ford", "BMW", "Tesla"]
        mock_colors = ["Silver", "Black", "White", "Blue", "Red"]
        
        # Detimere mock resultat baseret på nummerplade hash
        seed = sum(ord(c) for c in plate_number)
        brand = mock_brands[seed % len(mock_brands)]
        color = mock_colors[seed % len(mock_colors)]
        
        return {
            "plate": plate_number,
            "type": "Personbil",
            "status": "Registreret",
            "first_registration": "Unknown",
            "next_syn": "Unknown",
            "make": brand,
            "model": "Generic Model",
            "color": color,
            "fuel_type": "Unknown"
        }
