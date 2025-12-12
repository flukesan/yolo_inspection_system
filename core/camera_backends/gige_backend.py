"""
GigE Vision Camera Backend - รองรับ Industrial GigE Cameras
Backend for GigE Vision cameras using Harvesters (GenICam)
"""
import threading
import time
from typing import Optional, Dict, Any
import numpy as np
from .base_backend import BaseCameraBackend

try:
    from harvesters.core import Harvester
    HARVESTERS_AVAILABLE = True
except ImportError:
    HARVESTERS_AVAILABLE = False
    print("⚠ Harvesters ไม่ได้ติดตั้ง - GigE Vision ไม่สามารถใช้งานได้")


class GigEBackend(BaseCameraBackend):
    """Camera backend สำหรับ GigE Vision cameras (Harvesters/GenICam)"""

    def __init__(self):
        """Initialize GigE Vision backend"""
        super().__init__()

        if not HARVESTERS_AVAILABLE:
            raise RuntimeError("Harvesters library is not installed. Install with: pip install harvesters genicam")

        self.harvester: Optional[Harvester] = None
        self.image_acquirer = None
        self.is_running = False
        self.current_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()
        self.capture_thread: Optional[threading.Thread] = None

        # Statistics
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        self.fps_frame_count = 0

    def connect(self, source: Any, width: int = 1280, height: int = 720,
                fps: int = 30, **kwargs) -> bool:
        """
        เชื่อมต่อกล้อง GigE Vision

        Args:
            source: GenTL producer path หรือ camera serial number/IP
                   - ถ้าเป็น dict: {'gentl_path': '/path/to/producer.cti', 'camera_id': 'serial_or_ip'}
                   - ถ้าเป็น str: ถือว่าเป็น GenTL producer path
            width: Frame width (ถ้ากล้องรองรับ)
            height: Frame height (ถ้ากล้องรองรับ)
            fps: Target FPS (ถ้ากล้องรองรับ)
            **kwargs: Additional parameters
                - gentl_path: Path to GenTL producer (.cti file)
                - camera_id: Camera serial number, IP, or index (default: 0)
                - exposure_time: Exposure time in microseconds
                - gain: Camera gain

        Returns:
            True if successful
        """
        try:
            # Disconnect existing camera
            self.disconnect()

            # Parse source parameter
            gentl_path = None
            camera_id = 0

            if isinstance(source, dict):
                gentl_path = source.get('gentl_path')
                camera_id = source.get('camera_id', 0)
            elif isinstance(source, str):
                gentl_path = source
                camera_id = kwargs.get('camera_id', 0)

            # Get from kwargs if not in source
            if gentl_path is None:
                gentl_path = kwargs.get('gentl_path')

            if gentl_path is None:
                print("✗ ต้องระบุ GenTL producer path (.cti file)")
                print("  ตัวอย่าง: {'gentl_path': '/opt/pylon/lib/gentlproducer.cti', 'camera_id': 0}")
                return False

            print(f"กำลังเชื่อมต่อกล้อง GigE Vision...")
            print(f"  GenTL Producer: {gentl_path}")
            print(f"  Camera ID: {camera_id}")

            # Create Harvester and add GenTL producer
            self.harvester = Harvester()
            self.harvester.add_file(gentl_path)
            self.harvester.update()

            # Wait for device discovery to complete
            # GigE Vision uses broadcast discovery which may take time
            time.sleep(0.5)  # 500ms should be enough for network discovery

            # Check available devices
            if len(self.harvester.device_info_list) == 0:
                # Try one more time with longer timeout
                print("  รอให้ device discovery เสร็จ...")
                time.sleep(1.0)
                self.harvester.update()

            if len(self.harvester.device_info_list) == 0:
                print("✗ ไม่พบกล้อง GigE Vision")
                print("\n💡 วิธีแก้ไข:")
                print("  1. ตรวจสอบกล้องเชื่อมต่อกับ Ethernet แล้ว")
                print("  2. ตรวจสอบ PC และกล้องอยู่ใน subnet เดียวกัน (เช่น 192.168.1.x)")
                print("  3. ปิด Windows Firewall ชั่วคราวเพื่อทดสอบ")
                print("  4. ใช้ Pylon Viewer/Vimba Viewer ตรวจสอบว่าเห็นกล้องหรือไม่")
                return False

            print(f"✓ พบกล้อง {len(self.harvester.device_info_list)} ตัว:")
            for idx, device_info in enumerate(self.harvester.device_info_list):
                print(f"  [{idx}] {device_info}")

            # Create image acquirer
            try:
                if isinstance(camera_id, int):
                    # Use camera index
                    if camera_id >= len(self.harvester.device_info_list):
                        print(f"\n✗ Camera index {camera_id} ไม่ถูกต้อง (มีแค่ {len(self.harvester.device_info_list)} ตัว)")
                        print("💡 ลองใช้ Serial Number หรือ User ID แทน")
                        return False
                    print(f"→ กำลังเชื่อมต่อกล้อง index {camera_id}...")
                    self.image_acquirer = self.harvester.create(camera_id)
                else:
                    # Use serial number, user ID, or IP - try multiple methods
                    camera_id_str = str(camera_id)
                    print(f"→ กำลังค้นหากล้อง: {camera_id_str}...")

                    # Try 1: Serial Number
                    try:
                        print(f"  ลองใช้ Serial Number...")
                        self.image_acquirer = self.harvester.create({'serial_number': camera_id_str})
                    except:
                        # Try 2: User ID
                        try:
                            print(f"  ลองใช้ User ID...")
                            self.image_acquirer = self.harvester.create({'user_id': camera_id_str})
                        except:
                            # Try 3: IP Address
                            try:
                                print(f"  ลองใช้ IP Address...")
                                self.image_acquirer = self.harvester.create({'ip_address': camera_id_str})
                            except Exception as e:
                                print(f"\n✗ ไม่สามารถเชื่อมต่อกล้อง '{camera_id_str}'")
                                print(f"\n💡 วิธีแก้ไข:")
                                print(f"  กล้องที่พบ:")
                                for idx, dev in enumerate(self.harvester.device_info_list):
                                    print(f"    [{idx}] Serial: {getattr(dev, 'serial_number', 'N/A')}, "
                                          f"User ID: {getattr(dev, 'user_id', 'N/A')}, "
                                          f"IP: {getattr(dev, 'ip_address', 'N/A')}")
                                print(f"\n  ลองใช้ค่าดังนี้ใน Camera ID:")
                                print(f"    - Index: 0")
                                if hasattr(self.harvester.device_info_list[0], 'serial_number'):
                                    print(f"    - Serial Number: {self.harvester.device_info_list[0].serial_number}")
                                if hasattr(self.harvester.device_info_list[0], 'user_id'):
                                    print(f"    - User ID: {self.harvester.device_info_list[0].user_id}")
                                if hasattr(self.harvester.device_info_list[0], 'ip_address'):
                                    print(f"    - IP Address: {self.harvester.device_info_list[0].ip_address}")
                                raise
            except Exception as e:
                print(f"✗ Error creating image acquirer: {e}")
                return False

            # Configure camera parameters
            try:
                # Set Width/Height if supported
                if self.image_acquirer.remote_device.node_map.Width:
                    max_width = self.image_acquirer.remote_device.node_map.Width.max
                    self.image_acquirer.remote_device.node_map.Width.value = min(width, max_width)

                if self.image_acquirer.remote_device.node_map.Height:
                    max_height = self.image_acquirer.remote_device.node_map.Height.max
                    self.image_acquirer.remote_device.node_map.Height.value = min(height, max_height)

                # Set FPS if supported (AcquisitionFrameRate)
                try:
                    if hasattr(self.image_acquirer.remote_device.node_map, 'AcquisitionFrameRate'):
                        self.image_acquirer.remote_device.node_map.AcquisitionFrameRateEnable.value = True
                        self.image_acquirer.remote_device.node_map.AcquisitionFrameRate.value = fps
                except:
                    pass  # Not all cameras support frame rate control

                # Set Exposure if provided
                if 'exposure_time' in kwargs:
                    try:
                        self.image_acquirer.remote_device.node_map.ExposureTime.value = kwargs['exposure_time']
                    except:
                        pass

                # Set Gain if provided
                if 'gain' in kwargs:
                    try:
                        self.image_acquirer.remote_device.node_map.Gain.value = kwargs['gain']
                    except:
                        pass

            except Exception as e:
                print(f"⚠ บางการตั้งค่าไม่สามารถใช้งานได้: {e}")

            # Get actual settings
            actual_width = self.image_acquirer.remote_device.node_map.Width.value
            actual_height = self.image_acquirer.remote_device.node_map.Height.value

            device_info = self.harvester.device_info_list[camera_id if isinstance(camera_id, int) else 0]

            self.camera_info = {
                'backend': 'GigE Vision',
                'source': str(camera_id),
                'vendor': getattr(device_info, 'vendor', 'Unknown'),
                'model': getattr(device_info, 'model', 'Unknown'),
                'serial_number': getattr(device_info, 'serial_number', 'Unknown'),
                'width': actual_width,
                'height': actual_height,
                'pixel_format': self.image_acquirer.remote_device.node_map.PixelFormat.value
            }

            print(f"✓ เชื่อมต่อกล้องสำเร็จ (GigE Vision)")
            print(f"  Model: {self.camera_info['vendor']} {self.camera_info['model']}")
            print(f"  Resolution: {actual_width}x{actual_height}")
            print(f"  Pixel Format: {self.camera_info['pixel_format']}")

            # Start acquisition
            self.image_acquirer.start()

            # Start capture thread
            self.is_running = True
            self.is_connected_flag = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()

            return True

        except Exception as e:
            print(f"✗ Error connecting GigE camera: {e}")
            import traceback
            traceback.print_exc()
            return False

    def disconnect(self) -> None:
        """ตัดการเชื่อมต่อกล้อง"""
        self.is_running = False
        self.is_connected_flag = False

        if self.capture_thread is not None:
            self.capture_thread.join(timeout=2.0)
            self.capture_thread = None

        if self.image_acquirer is not None:
            try:
                self.image_acquirer.stop()
                self.image_acquirer.destroy()
            except:
                pass
            self.image_acquirer = None

        if self.harvester is not None:
            try:
                self.harvester.reset()
            except:
                pass
            self.harvester = None

        self.current_frame = None
        print("✓ ตัดการเชื่อมต่อกล้อง (GigE Vision)")

    def _capture_loop(self) -> None:
        """Background thread สำหรับอ่านภาพจากกล้อง"""
        while self.is_running and self.image_acquirer is not None:
            try:
                # Fetch buffer with timeout
                with self.image_acquirer.fetch(timeout=1.0) as buffer:
                    # Get numpy array from buffer
                    component = buffer.payload.components[0]
                    frame = component.data.reshape(component.height, component.width, -1)

                    # Convert to BGR if needed (most cameras use Mono or RGB8)
                    if len(frame.shape) == 2:  # Mono
                        frame = np.stack([frame] * 3, axis=-1)
                    elif frame.shape[2] == 1:  # Mono with channel
                        frame = np.repeat(frame, 3, axis=2)
                    elif frame.shape[2] == 3:  # RGB
                        # Convert RGB to BGR for OpenCV compatibility
                        frame = frame[:, :, ::-1]

                    # Ensure uint8
                    if frame.dtype != np.uint8:
                        frame = (frame / frame.max() * 255).astype(np.uint8)

                    with self.frame_lock:
                        self.current_frame = frame.copy()
                        self.frame_count += 1

                    # Calculate FPS
                    self.fps_frame_count += 1
                    current_time = time.time()
                    elapsed = current_time - self.last_fps_time

                    if elapsed >= 1.0:
                        self.fps = self.fps_frame_count / elapsed
                        self.fps_frame_count = 0
                        self.last_fps_time = current_time

            except Exception as e:
                if self.is_running:  # Only print if still supposed to be running
                    print(f"⚠ Timeout or error fetching frame: {e}")
                time.sleep(0.01)

    def get_frame(self) -> Optional[np.ndarray]:
        """
        ดึงภาพล่าสุดจากกล้อง

        Returns:
            Frame หรือ None ถ้าไม่มี
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None

    def is_connected(self) -> bool:
        """
        ตรวจสอบว่ากล้องเชื่อมต่ออยู่หรือไม่

        Returns:
            True if connected
        """
        return self.image_acquirer is not None and self.is_running

    def get_info(self) -> Dict[str, Any]:
        """
        ดึงข้อมูลกล้อง

        Returns:
            Camera information dictionary
        """
        return {
            **self.camera_info,
            'connected': self.is_connected(),
            'frame_count': self.frame_count,
            'current_fps': round(self.fps, 1)
        }

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.disconnect()
