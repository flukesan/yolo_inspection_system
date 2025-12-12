"""
Test GigE Vision Camera Connection with Harvesters
ทดสอบการเชื่อมต่อกล้อง GigE Vision

Run this script to diagnose connection issues
"""
import sys
import os

print("=" * 60)
print("GigE Vision Camera Connection Test")
print("=" * 60)

# Test 1: Check Harvesters installation
print("\n[Test 1] ตรวจสอบ Harvesters library...")
try:
    from harvesters.core import Harvester
    print("✓ Harvesters imported successfully")
except ImportError as e:
    print(f"✗ Cannot import Harvesters: {e}")
    print("  Run: pip install harvesters genicam")
    sys.exit(1)

# Test 2: Check GenTL Producer file
print("\n[Test 2] ตรวจสอบ GenTL Producer file...")
gentl_paths = [
    r"C:\Program Files\Basler\pylon 7\Runtime\x64\ProducerGEV.cti",
    r"C:/Program Files/Basler/pylon 7/Runtime/x64/ProducerGEV.cti",
    r"C:\Program Files\Basler\pylon\Runtime\x64\ProducerGEV.cti",
]

gentl_path = None
for path in gentl_paths:
    if os.path.exists(path):
        gentl_path = path
        print(f"✓ พบไฟล์: {path}")
        break
    else:
        print(f"  ไม่พบ: {path}")

if gentl_path is None:
    print("\n✗ ไม่พบ GenTL Producer file!")
    print("  กรุณาระบุ path ที่ถูกต้อง")
    gentl_path = input("  Enter GenTL Producer path: ").strip()
    if not os.path.exists(gentl_path):
        print("✗ File not found!")
        sys.exit(1)

# Test 3: Create Harvester
print("\n[Test 3] สร้าง Harvester object...")
try:
    h = Harvester()
    print("✓ Harvester created")
except Exception as e:
    print(f"✗ Error creating Harvester: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Load GenTL Producer
print(f"\n[Test 4] โหลด GenTL Producer...")
print(f"  Path: {gentl_path}")
try:
    h.add_file(gentl_path)
    print("✓ GenTL Producer loaded")
except Exception as e:
    print(f"✗ Error loading GenTL Producer: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Update device list
print("\n[Test 5] ค้นหากล้อง...")
try:
    h.update()
    print(f"✓ Device list updated")
except Exception as e:
    print(f"✗ Error updating device list: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Show detected cameras
print(f"\n[Test 6] แสดงกล้องที่พบ...")
print(f"จำนวนกล้อง: {len(h.device_info_list)}")

if len(h.device_info_list) == 0:
    print("\n✗ ไม่พบกล้อง!")
    print("\n💡 สาเหตุที่เป็นไปได้:")
    print("  1. Windows Firewall บลอก UDP packets")
    print("  2. Antivirus software บลอก Harvesters")
    print("  3. Python 32-bit/64-bit mismatch กับ Pylon SDK")
    print("  4. Harvesters ไม่สามารถเข้าถึง network interface")
    print("  5. ต้อง run as Administrator")
    print("\n💡 วิธีแก้:")
    print("  1. ปิด Windows Firewall ชั่วคราว")
    print("  2. ปิด Antivirus ชั่วคราว")
    print("  3. Run script นี้ด้วย Administrator")
    print("  4. ตรวจสอบ Python version (ต้องเป็น 64-bit)")

    # Check Python architecture
    import platform
    print(f"\n  Python version: {sys.version}")
    print(f"  Python architecture: {platform.architecture()[0]}")
    print(f"  Pylon SDK ต้องเป็น 64-bit เหมือนกัน")

    h.reset()
    sys.exit(1)

print(f"✓ พบกล้อง {len(h.device_info_list)} ตัว:\n")

for idx, device_info in enumerate(h.device_info_list):
    print(f"[{idx}] {device_info}")
    print(f"    Details:")

    # Show all available attributes
    for attr in dir(device_info):
        if not attr.startswith('_'):
            try:
                value = getattr(device_info, attr)
                if not callable(value):
                    print(f"      {attr}: {value}")
            except:
                pass
    print()

# Test 7: Try to connect to first camera
if len(h.device_info_list) > 0:
    print(f"\n[Test 7] ลองเชื่อมต่อกล้องตัวแรก (index 0)...")
    try:
        ia = h.create(0)
        print("✓ เชื่อมต่อสำเร็จ!")
        print(f"  Camera: {ia.remote_device.node_map.DeviceModelName.value}")

        # Try to grab a frame
        print("\n[Test 8] ลองจับภาพ...")
        try:
            ia.start()
            print("✓ Started acquisition")

            with ia.fetch(timeout=2.0) as buffer:
                print("✓ ได้ภาพแล้ว!")
                print(f"  Image size: {buffer.payload.components[0].width} x {buffer.payload.components[0].height}")

            ia.stop()
            print("✓ Stopped acquisition")

        except Exception as e:
            print(f"✗ Error grabbing frame: {e}")
            import traceback
            traceback.print_exc()

        ia.destroy()
        print("✓ Camera disconnected")

    except Exception as e:
        print(f"✗ Error connecting to camera: {e}")
        import traceback
        traceback.print_exc()

# Cleanup
print("\n[Cleanup] ปิดการเชื่อมต่อ...")
h.reset()
print("✓ Done")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
print("\nถ้าผ่านทุก test แต่ระบบหลักยังไม่ได้:")
print("  - ตรวจสอบ permissions ของ main application")
print("  - ลอง run application as Administrator")
print("  - ตรวจสอบ error logs ใน console")
