"""
PLC Communication - เชื่อมต่อกับ PLC
PLC communication via Modbus TCP
"""
from typing import Optional, Dict, Any
import time


class PLCCommunication:
    """สื่อสารกับ PLC ผ่าน Modbus TCP"""

    def __init__(self, ip: str = "192.168.1.10", port: int = 502, unit_id: int = 1):
        """
        Initialize PLC Communication

        Args:
            ip: PLC IP address
            port: Modbus TCP port
            unit_id: Modbus unit ID
        """
        self.ip = ip
        self.port = port
        self.unit_id = unit_id
        self.client = None
        self.is_connected = False

        # Modbus addresses
        self.trigger_address = 0  # Address for trigger signal
        self.result_address = 1   # Address for result (OK/NG)

    def connect(self) -> bool:
        """
        เชื่อมต่อ PLC

        Returns:
            True if successful
        """
        try:
            from pymodbus.client import ModbusTcpClient

            print(f"กำลังเชื่อมต่อ PLC: {self.ip}:{self.port}")

            self.client = ModbusTcpClient(
                host=self.ip,
                port=self.port,
                timeout=3
            )

            self.is_connected = self.client.connect()

            if self.is_connected:
                print(f"✓ เชื่อมต่อ PLC สำเร็จ")
            else:
                print(f"✗ ไม่สามารถเชื่อมต่อ PLC")

            return self.is_connected

        except ImportError:
            print("✗ กรุณาติดตั้ง pymodbus: pip install pymodbus")
            return False
        except Exception as e:
            print(f"✗ Error connecting to PLC: {e}")
            return False

    def disconnect(self) -> None:
        """ตัดการเชื่อมต่อ PLC"""
        if self.client is not None:
            self.client.close()
            self.is_connected = False
            print("✓ ตัดการเชื่อมต่อ PLC")

    def read_trigger(self) -> bool:
        """
        อ่านสัญญาณ trigger จาก PLC

        Returns:
            True if trigger is active
        """
        if not self.is_connected or self.client is None:
            return False

        try:
            response = self.client.read_coils(
                address=self.trigger_address,
                count=1,
                slave=self.unit_id
            )

            if not response.isError():
                return response.bits[0]

            return False

        except Exception as e:
            print(f"✗ Error reading trigger: {e}")
            return False

    def write_result(self, is_ok: bool) -> bool:
        """
        เขียนผลการตรวจสอบไปยัง PLC

        Args:
            is_ok: True for OK, False for NG

        Returns:
            True if successful
        """
        if not self.is_connected or self.client is None:
            return False

        try:
            response = self.client.write_coil(
                address=self.result_address,
                value=is_ok,
                slave=self.unit_id
            )

            return not response.isError()

        except Exception as e:
            print(f"✗ Error writing result: {e}")
            return False

    def read_register(self, address: int, count: int = 1) -> Optional[list]:
        """
        อ่าน holding registers

        Args:
            address: Register address
            count: Number of registers

        Returns:
            List of register values or None
        """
        if not self.is_connected or self.client is None:
            return None

        try:
            response = self.client.read_holding_registers(
                address=address,
                count=count,
                slave=self.unit_id
            )

            if not response.isError():
                return response.registers

            return None

        except Exception as e:
            print(f"✗ Error reading register: {e}")
            return None

    def write_register(self, address: int, value: int) -> bool:
        """
        เขียน holding register

        Args:
            address: Register address
            value: Value to write

        Returns:
            True if successful
        """
        if not self.is_connected or self.client is None:
            return False

        try:
            response = self.client.write_register(
                address=address,
                value=value,
                slave=self.unit_id
            )

            return not response.isError()

        except Exception as e:
            print(f"✗ Error writing register: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        ดึงสถานะการเชื่อมต่อ

        Returns:
            Status dictionary
        """
        return {
            'connected': self.is_connected,
            'ip': self.ip,
            'port': self.port,
            'unit_id': self.unit_id
        }
