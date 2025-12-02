"""
Database - จัดการฐานข้อมูล SQLite/MySQL
Database management for inspection records
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


class Database:
    """จัดการฐานข้อมูล SQLite"""

    def __init__(self, db_path: str = "data/inspection.db"):
        """
        Initialize Database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

        # Create database directory
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self.connect()
        self.create_tables()

    def connect(self) -> bool:
        """เชื่อมต่อฐานข้อมูล"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            print(f"✓ เชื่อมต่อฐานข้อมูล: {self.db_path}")
            return True
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return False

    def create_tables(self) -> None:
        """สร้างตารางในฐานข้อมูล"""
        try:
            cursor = self.conn.cursor()

            # Inspections table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inspections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    num_defects INTEGER DEFAULT 0,
                    detection_time_ms REAL DEFAULT 0,
                    image_path TEXT,
                    detections TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Defects table (detailed defect records)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS defects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inspection_id INTEGER,
                    class_id INTEGER,
                    class_name TEXT,
                    confidence REAL,
                    bbox_x1 INTEGER,
                    bbox_y1 INTEGER,
                    bbox_x2 INTEGER,
                    bbox_y2 INTEGER,
                    center_x INTEGER,
                    center_y INTEGER,
                    FOREIGN KEY (inspection_id) REFERENCES inspections (id)
                )
            ''')

            # Statistics table (daily/hourly aggregates)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    hour INTEGER,
                    total_inspections INTEGER DEFAULT 0,
                    total_ok INTEGER DEFAULT 0,
                    total_defects INTEGER DEFAULT 0,
                    defect_rate REAL DEFAULT 0,
                    avg_detection_time_ms REAL DEFAULT 0,
                    UNIQUE(date, hour)
                )
            ''')

            self.conn.commit()
            print("✓ สร้างตารางฐานข้อมูล")

        except Exception as e:
            print(f"✗ Error creating tables: {e}")

    def insert_inspection(self, data: Dict[str, Any]) -> Optional[int]:
        """
        บันทึกผลการตรวจสอบ

        Args:
            data: Inspection data

        Returns:
            Inspection ID
        """
        try:
            cursor = self.conn.cursor()

            timestamp = data.get('timestamp', datetime.now())
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()

            # Insert inspection record
            cursor.execute('''
                INSERT INTO inspections
                (timestamp, status, num_defects, detection_time_ms, image_path, detections)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                data.get('status', 'UNKNOWN'),
                data.get('num_defects', 0),
                data.get('detection_time_ms', 0),
                data.get('image_path', ''),
                json.dumps(data.get('detections', []), ensure_ascii=False)
            ))

            inspection_id = cursor.lastrowid

            # Insert defect records
            detections = data.get('detections', [])
            for det in detections:
                cursor.execute('''
                    INSERT INTO defects
                    (inspection_id, class_id, class_name, confidence,
                     bbox_x1, bbox_y1, bbox_x2, bbox_y2, center_x, center_y)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    inspection_id,
                    det.get('class_id', 0),
                    det.get('class_name', ''),
                    det.get('confidence', 0),
                    det['bbox'][0] if 'bbox' in det else 0,
                    det['bbox'][1] if 'bbox' in det else 0,
                    det['bbox'][2] if 'bbox' in det else 0,
                    det['bbox'][3] if 'bbox' in det else 0,
                    det['center'][0] if 'center' in det else 0,
                    det['center'][1] if 'center' in det else 0
                ))

            self.conn.commit()
            return inspection_id

        except Exception as e:
            print(f"✗ Error inserting inspection: {e}")
            return None

    def get_inspections(self, limit: int = 100, offset: int = 0,
                       status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        ดึงข้อมูลการตรวจสอบ

        Args:
            limit: จำนวนแถวสูงสุด
            offset: Offset
            status: Filter by status (OK, NG)

        Returns:
            List of inspection records
        """
        try:
            cursor = self.conn.cursor()

            query = "SELECT * FROM inspections"
            params = []

            if status:
                query += " WHERE status = ?"
                params.append(status)

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'status': row['status'],
                    'num_defects': row['num_defects'],
                    'detection_time_ms': row['detection_time_ms'],
                    'image_path': row['image_path'],
                    'detections': json.loads(row['detections']) if row['detections'] else []
                })

            return results

        except Exception as e:
            print(f"✗ Error getting inspections: {e}")
            return []

    def get_statistics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        ดึงสถิติ

        Args:
            start_date: วันที่เริ่มต้น (YYYY-MM-DD)
            end_date: วันที่สิ้นสุด (YYYY-MM-DD)

        Returns:
            Statistics dictionary
        """
        try:
            cursor = self.conn.cursor()

            query = "SELECT COUNT(*) as total, SUM(CASE WHEN status='OK' THEN 1 ELSE 0 END) as ok, SUM(CASE WHEN status='NG' THEN 1 ELSE 0 END) as ng FROM inspections"
            params = []

            if start_date and end_date:
                query += " WHERE date(timestamp) BETWEEN ? AND ?"
                params.extend([start_date, end_date])

            cursor.execute(query, params)
            row = cursor.fetchone()

            total = row['total'] or 0
            ok = row['ok'] or 0
            ng = row['ng'] or 0
            defect_rate = (ng / total * 100) if total > 0 else 0

            return {
                'total': total,
                'ok': ok,
                'ng': ng,
                'defect_rate': round(defect_rate, 2)
            }

        except Exception as e:
            print(f"✗ Error getting statistics: {e}")
            return {'total': 0, 'ok': 0, 'ng': 0, 'defect_rate': 0}

    def close(self) -> None:
        """ปิดการเชื่อมต่อฐานข้อมูล"""
        if self.conn:
            self.conn.close()
            print("✓ ปิดการเชื่อมต่อฐานข้อมูล")
