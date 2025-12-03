"""
Debug Qt Installation
ตรวจสอบการติดตั้ง Qt และ PyQt6
"""
import sys
import os

def main():
    print("=" * 70)
    print("  Qt/PyQt6 Debug Information")
    print("=" * 70)
    print()

    # Python info
    print("[1] Python Information:")
    print(f"  Version: {sys.version}")
    print(f"  Executable: {sys.executable}")
    print()

    # Try to import PyQt6
    print("[2] PyQt6 Import Test:")
    try:
        import PyQt6
        print("  ✓ PyQt6 imported successfully")
        print(f"  Location: {PyQt6.__file__}")
        print()

        # Qt version
        from PyQt6 import QtCore
        print("[3] Qt Information:")
        print(f"  Qt Version: {QtCore.QT_VERSION_STR}")
        print(f"  PyQt Version: {QtCore.PYQT_VERSION_STR}")
        print()

        # Plugins path
        print("[4] Qt Plugins:")
        try:
            # PyQt6 uses path() instead of location()
            from PyQt6.QtCore import QLibraryInfo
            plugins_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
            print(f"  Plugins Path: {plugins_path}")

            if os.path.exists(plugins_path):
                print("  ✓ Plugins path exists")

                # Check platforms folder
                platforms_path = os.path.join(plugins_path, 'platforms')
                if os.path.exists(platforms_path):
                    print(f"  ✓ Platforms folder exists: {platforms_path}")
                    plugins = os.listdir(platforms_path)
                    print(f"  Platform plugins found: {', '.join(plugins)}")

                    # Check for platform plugin (qwindows.dll on Windows, libqxcb.so on Linux)
                    if sys.platform == 'win32':
                        if 'qwindows.dll' in plugins:
                            print("  ✓ qwindows.dll found (Windows platform plugin)")
                        else:
                            print("  ✗ qwindows.dll NOT found!")
                            print("    This is the problem!")
                    elif sys.platform == 'linux':
                        if any('qxcb' in p for p in plugins):
                            print("  ✓ qxcb plugin found (Linux platform plugin)")
                        else:
                            print("  ✗ qxcb plugin NOT found!")
                    else:
                        print(f"  Platform plugins: {', '.join(plugins)}")
                else:
                    print(f"  ✗ Platforms folder NOT found: {platforms_path}")
            else:
                print("  ✗ Plugins path does NOT exist!")
        except Exception as e:
            print(f"  ✗ Error checking plugins: {e}")
        print()

        # Try to create QApplication
        print("[5] QApplication Test:")
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication(sys.argv)
            print("  ✓ QApplication created successfully")
            print()
            print("=" * 70)
            print("  RESULT: PyQt6 is working correctly!")
            print("=" * 70)
        except Exception as e:
            print(f"  ✗ Failed to create QApplication: {e}")
            print()
            print("=" * 70)
            print("  RESULT: PyQt6 has issues!")
            print("  Solution: Reinstall PyQt6")
            print("    pip uninstall PyQt6 -y")
            print("    pip install PyQt6")
            print("=" * 70)

    except ImportError as e:
        print(f"  ✗ Failed to import PyQt6: {e}")
        print()
        print("=" * 70)
        print("  RESULT: PyQt6 is NOT installed!")
        print("  Solution: Install PyQt6")
        print("    pip install PyQt6")
        print("=" * 70)
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    print()
    input("Press Enter to exit...")
