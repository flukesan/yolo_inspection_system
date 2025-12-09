"""
MQTT Client - เชื่อมต่อและส่งข้อมูลไปยัง MQTT Broker (DeviceWise)
Connects to MQTT broker and publishes inspection results
"""
import json
import time
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime


class MQTTClient:
    """MQTT Client สำหรับส่งข้อมูลการตรวจสอบ"""

    def __init__(self, broker_host: str = "localhost", port: int = 1883,
                 client_id: str = None, username: str = None, password: str = None,
                 timeout: int = 3, heartbeat_interval: int = 60):
        """
        Initialize MQTT Client

        Args:
            broker_host: MQTT broker hostname/IP
            port: MQTT broker port (default: 1883)
            client_id: Client ID (if None, will generate from MAC address)
            username: MQTT username (optional)
            password: MQTT password (optional)
            timeout: Connection timeout in seconds
            heartbeat_interval: Keep-alive interval in seconds
        """
        self.broker_host = broker_host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.heartbeat_interval = heartbeat_interval

        # Generate client ID if not provided
        if client_id is None:
            self.client_id = self._generate_client_id()
        else:
            self.client_id = client_id

        # MQTT client
        self.client = None
        self.connected = False

        # Statistics
        self.total_published = 0
        self.last_publish_time = None

        # Callbacks
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None
        self.on_publish_callback: Optional[Callable] = None

    def _generate_client_id(self) -> str:
        """สร้าง Client ID จาก MAC Address หรือ UUID"""
        try:
            import getmac
            mac = getmac.get_mac_address()
            if mac:
                return f"yolo_inspection_{mac.replace(':', '')}"
        except:
            pass

        # Fallback to UUID
        return f"yolo_inspection_{uuid.uuid4().hex[:12]}"

    def connect(self) -> bool:
        """
        เชื่อมต่อกับ MQTT Broker

        Returns:
            True if connected successfully
        """
        try:
            # Try to import paho-mqtt
            try:
                import paho.mqtt.client as mqtt
            except ImportError:
                print("✗ กรุณาติดตั้ง paho-mqtt: pip install paho-mqtt")
                return False

            # Create MQTT client
            self.client = mqtt.Client(client_id=self.client_id, clean_session=True)

            # Set username and password if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)

            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish

            # Connect to broker
            print(f"กำลังเชื่อมต่อ MQTT Broker: {self.broker_host}:{self.port}")
            self.client.connect(self.broker_host, self.port, self.heartbeat_interval)

            # Start network loop in background
            self.client.loop_start()

            # Wait a bit for connection
            time.sleep(0.5)

            if self.connected:
                print(f"✓ เชื่อมต่อ MQTT Broker สำเร็จ (Client ID: {self.client_id})")
                return True
            else:
                print("✗ ไม่สามารถเชื่อมต่อ MQTT Broker ได้")
                return False

        except Exception as e:
            print(f"✗ Error connecting to MQTT Broker: {e}")
            return False

    def disconnect(self) -> bool:
        """
        ตัดการเชื่อมต่อ MQTT Broker

        Returns:
            True if disconnected successfully
        """
        try:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
                self.connected = False
                print("✓ ตัดการเชื่อมต่อ MQTT Broker แล้ว")
            return True
        except Exception as e:
            print(f"✗ Error disconnecting MQTT: {e}")
            return False

    def publish_inspection_result(self, model_name: str, status: str,
                                   defects: list, topic: str = "yolo/inspection") -> bool:
        """
        Publish ผลการตรวจสอบไปยัง MQTT Broker

        Args:
            model_name: ชื่อโมเดลที่ใช้ตรวจสอบ
            status: สถานะ (OK/NG)
            defects: รายการ defects ที่พบ
            topic: MQTT topic

        Returns:
            True if published successfully
        """
        if not self.connected:
            print("! MQTT ไม่ได้เชื่อมต่อ")
            return False

        try:
            # Prepare payload
            payload = {
                "timestamp": datetime.now().isoformat(),
                "model_name": model_name,
                "status": status,
                "defects": self._prepare_defects_data(defects)
            }

            # Convert to JSON
            message = json.dumps(payload, ensure_ascii=False)

            # Publish
            result = self.client.publish(topic, message, qos=1)

            # Wait for publish to complete
            result.wait_for_publish()

            if result.is_published():
                self.total_published += 1
                self.last_publish_time = time.time()
                print(f"✓ Published to MQTT: {topic} - Status: {status}")
                return True
            else:
                print(f"✗ Failed to publish to MQTT")
                return False

        except Exception as e:
            print(f"✗ Error publishing to MQTT: {e}")
            return False

    def _prepare_defects_data(self, detections: list) -> dict:
        """
        เตรียมข้อมูล defects สำหรับ publish

        Args:
            detections: รายการ detections

        Returns:
            Dictionary ของข้อมูล defects
        """
        # Count defects by class
        defect_counts = {}
        defect_list = []

        for detection in detections:
            class_name = detection.get('class_name', 'Unknown')
            confidence = detection.get('confidence', 0)

            # Count
            defect_counts[class_name] = defect_counts.get(class_name, 0) + 1

            # Add to list
            defect_list.append({
                "type": class_name,
                "confidence": round(confidence, 2)
            })

        return {
            "total_count": len(detections),
            "defect_types": defect_counts,
            "details": defect_list
        }

    def _on_connect(self, client, userdata, flags, rc):
        """Callback เมื่อเชื่อมต่อสำเร็จ"""
        if rc == 0:
            self.connected = True
            print(f"✓ MQTT Connected (Code: {rc})")
            if self.on_connect_callback:
                self.on_connect_callback()
        else:
            self.connected = False
            print(f"✗ MQTT Connection failed (Code: {rc})")

    def _on_disconnect(self, client, userdata, rc):
        """Callback เมื่อตัดการเชื่อมต่อ"""
        self.connected = False
        print(f"! MQTT Disconnected (Code: {rc})")
        if self.on_disconnect_callback:
            self.on_disconnect_callback()

    def _on_publish(self, client, userdata, mid):
        """Callback เมื่อ publish สำเร็จ"""
        if self.on_publish_callback:
            self.on_publish_callback(mid)

    def is_connected(self) -> bool:
        """ตรวจสอบสถานะการเชื่อมต่อ"""
        return self.connected

    def get_stats(self) -> Dict[str, Any]:
        """
        ดึงสถิติการใช้งาน MQTT

        Returns:
            Statistics dictionary
        """
        return {
            'connected': self.connected,
            'broker_host': self.broker_host,
            'port': self.port,
            'client_id': self.client_id,
            'total_published': self.total_published,
            'last_publish_time': self.last_publish_time
        }
