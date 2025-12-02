"""
Report Generator - สร้างรายงาน
Generate inspection reports in Excel/PDF format
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json


class ReportGenerator:
    """สร้างรายงานการตรวจสอบ"""

    def __init__(self, database=None, output_dir: str = "reports"):
        """
        Initialize Report Generator

        Args:
            database: Database instance
            output_dir: Output directory for reports
        """
        self.database = database
        self.output_dir = output_dir

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def generate_excel_report(self, start_date: str = None, end_date: str = None,
                             filename: str = None) -> str:
        """
        สร้างรายงาน Excel

        Args:
            start_date: วันที่เริ่มต้น (YYYY-MM-DD)
            end_date: วันที่สิ้นสุด (YYYY-MM-DD)
            filename: Output filename

        Returns:
            Path to generated report
        """
        try:
            import pandas as pd

            # Generate filename
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"inspection_report_{timestamp}.xlsx"

            filepath = os.path.join(self.output_dir, filename)

            # Get data from database
            if self.database is None:
                print("! Database not configured")
                return ""

            inspections = self.database.get_inspections(limit=10000)
            statistics = self.database.get_statistics(start_date, end_date)

            # Filter by date range
            if start_date or end_date:
                inspections = [
                    insp for insp in inspections
                    if self._is_in_date_range(insp['timestamp'], start_date, end_date)
                ]

            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['Total Inspections', 'OK Count', 'NG Count', 'Defect Rate (%)'],
                    'Value': [
                        statistics['total'],
                        statistics['ok'],
                        statistics['ng'],
                        statistics['defect_rate']
                    ]
                }
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)

                # Inspections sheet
                if inspections:
                    df_inspections = pd.DataFrame(inspections)
                    df_inspections.to_excel(writer, sheet_name='Inspections', index=False)

                # Defects by class sheet
                defect_counts = self._count_defects_by_class(inspections)
                if defect_counts:
                    df_defects = pd.DataFrame(
                        list(defect_counts.items()),
                        columns=['Defect Class', 'Count']
                    )
                    df_defects.to_excel(writer, sheet_name='Defects by Class', index=False)

            print(f"✓ สร้างรายงาน Excel: {filepath}")
            return filepath

        except ImportError:
            print("✗ กรุณาติดตั้ง pandas และ openpyxl: pip install pandas openpyxl")
            return ""
        except Exception as e:
            print(f"✗ Error generating Excel report: {e}")
            return ""

    def generate_daily_report(self, date: str = None) -> str:
        """
        สร้างรายงานประจำวัน

        Args:
            date: วันที่ (YYYY-MM-DD), ถ้าไม่ระบุจะใช้วันนี้

        Returns:
            Path to generated report
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        filename = f"daily_report_{date}.xlsx"
        return self.generate_excel_report(start_date=date, end_date=date, filename=filename)

    def generate_weekly_report(self) -> str:
        """
        สร้างรายงานประจำสัปดาห์

        Returns:
            Path to generated report
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        filename = f"weekly_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"

        return self.generate_excel_report(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            filename=filename
        )

    def generate_monthly_report(self, year: int = None, month: int = None) -> str:
        """
        สร้างรายงานประจำเดือน

        Args:
            year: ปี
            month: เดือน

        Returns:
            Path to generated report
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        filename = f"monthly_report_{year}_{month:02d}.xlsx"

        return self.generate_excel_report(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            filename=filename
        )

    def _is_in_date_range(self, timestamp_str: str, start_date: str = None,
                         end_date: str = None) -> bool:
        """ตรวจสอบว่า timestamp อยู่ในช่วงวันที่ที่กำหนดหรือไม่"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            date_str = timestamp.strftime("%Y-%m-%d")

            if start_date and date_str < start_date:
                return False
            if end_date and date_str > end_date:
                return False

            return True

        except:
            return True

    def _count_defects_by_class(self, inspections: List[Dict[str, Any]]) -> Dict[str, int]:
        """นับจำนวน defect แยกตาม class"""
        counts = {}

        for insp in inspections:
            detections = insp.get('detections', [])
            for det in detections:
                class_name = det.get('class_name', 'Unknown')
                counts[class_name] = counts.get(class_name, 0) + 1

        return counts
