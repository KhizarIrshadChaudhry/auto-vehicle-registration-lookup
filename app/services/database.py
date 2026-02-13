import sqlite3
import datetime
import json
from app.config import settings
import os

class DatabaseService:
    def __init__(self):
        os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        """Initialize tables if they don't exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS plate_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                confidence REAL,
                input_source TEXT,
                vehicle_info TEXT
            )
        ''')
        self.conn.commit()
        self._ensure_columns()

    def insert_plate(self, plate_text, confidence, source, vehicle_info="Unknown"):
        try:
            timestamp = datetime.datetime.now()
            serialized_vehicle_info = self._serialize_vehicle_info(vehicle_info)
            vehicle_fields = self._extract_vehicle_fields(vehicle_info)
            self.cursor.execute('''
                INSERT INTO plate_events (
                    plate_number,
                    timestamp,
                    confidence,
                    input_source,
                    vehicle_info,
                    vehicle_type,
                    vehicle_status,
                    first_registration,
                    next_syn,
                    make,
                    model,
                    color,
                    fuel_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plate_text,
                timestamp,
                confidence,
                source,
                serialized_vehicle_info,
                vehicle_fields["vehicle_type"],
                vehicle_fields["vehicle_status"],
                vehicle_fields["first_registration"],
                vehicle_fields["next_syn"],
                vehicle_fields["make"],
                vehicle_fields["model"],
                vehicle_fields["color"],
                vehicle_fields["fuel_type"],
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False

    def get_recent_plates(self, limit=10):
        self.cursor.execute('SELECT plate_number, timestamp, vehicle_info FROM plate_events ORDER BY id DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def _serialize_vehicle_info(self, vehicle_info):
        if isinstance(vehicle_info, (dict, list)):
            return json.dumps(vehicle_info, ensure_ascii=False)
        return str(vehicle_info)

    def _extract_vehicle_fields(self, vehicle_info):
        if isinstance(vehicle_info, dict):
            return {
                "vehicle_type": vehicle_info.get("type"),
                "vehicle_status": vehicle_info.get("status"),
                "first_registration": vehicle_info.get("first_registration"),
                "next_syn": vehicle_info.get("next_syn"),
                "make": vehicle_info.get("make"),
                "model": vehicle_info.get("model"),
                "color": vehicle_info.get("color"),
                "fuel_type": vehicle_info.get("fuel_type"),
            }

        return {
            "vehicle_type": None,
            "vehicle_status": None,
            "first_registration": None,
            "next_syn": None,
            "make": None,
            "model": None,
            "color": None,
            "fuel_type": None,
        }

    def _ensure_columns(self):
        desired_columns = {
            "vehicle_type": "TEXT",
            "vehicle_status": "TEXT",
            "first_registration": "TEXT",
            "next_syn": "TEXT",
            "make": "TEXT",
            "model": "TEXT",
            "color": "TEXT",
            "fuel_type": "TEXT",
        }
        self.cursor.execute("PRAGMA table_info(plate_events)")
        existing = {row[1] for row in self.cursor.fetchall()}

        for column_name, column_type in desired_columns.items():
            if column_name not in existing:
                self.cursor.execute(
                    f"ALTER TABLE plate_events ADD COLUMN {column_name} {column_type}"
                )

        self.conn.commit()

    def close(self):
        self.conn.close()
