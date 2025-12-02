"""
Debug Qt Installation
ตรวจสอบการติดตั้ง Qt และ PyQt5
"""
import sys
import os

def main():
    print("=" * 70)
    print("  Qt/PyQt5 Debug Information")
    print("=" * 70)
    print()

    # Python info
    print("[1] Python Information:")
    print(f"  Version: {sys.version}")
    print(f"  Executable: {sys.executable}")
    print()

    # Try to import PyQt5
    print("[2] PyQt5 Import Test:")
    try:
        import PyQt5
        print("  ✓ PyQt5 imported successfully")
        print(f"  Location: {PyQt5.__file__}")
        print(f"  Version: {PyQt5.QtCore.PYQT_VERSION_STR}")
        print()

        # Qt version
        from PyQt5 import QtCore
        print("[3] Qt Information:")
        print(f"  Qt Version: {QtCore.QT_VERSION_STR}")
        print(f"  PyQt Version: {PyQt5.QtCore.PYQT_VERSION_STR}")
        print()

        # Plugins path
        print("[4] Qt Plugins:")
        plugins_path = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.PluginsPath)
        print(f"  Plugins Path: {plugins_path}")

        if os.path.exists(plugins_path):
            print("  ✓ Plugins path exists")

            # Check platforms folder
            platforms_path = os.path.join(plugins_path, 'platforms')
            if os.path.exists(platforms_path):
                print(f"  ✓ Platforms folder exists: {platforms_path}")
                plugins = os.listdir(platforms_path)
                print(f"  Platform plugins found: {', '.join(plugins)}")

                # Check for windows plugin
                if 'qwindows.dll' in plugins:
                    print("  ✓ qwindows.dll found (Windows platform plugin)")
                else:
                    print("  ✗ qwindows.dll NOT found!")
                    print("    This is the problem!")
            else:
                print(f"  ✗ Platforms folder NOT found: {platforms_path}")
        else:
            print("  ✗ Plugins path does NOT exist!")
        print()

        # Try to create QApplication
        print("[5] QApplication Test:")
        try:
            from PyQt5.QtWidgets import QApplication
            app = QApplication(sys.argv)
            print("  ✓ QApplication created successfully")
            print()
            print("=" * 70)
            print("  RESULT: PyQt5 is working correctly!")
            print("=" * 70)
        except Exception as e:
            print(f"  ✗ Failed to create QApplication: {e}")
            print()
            print("=" * 70)
            print("  RESULT: PyQt5 has issues!")
            print("  Solution: Reinstall PyQt5")
            print("    pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip -y")
            print("    pip install PyQt5==5.15.9")
            print("=" * 70)

    except ImportError as e:
        print(f"  ✗ Failed to import PyQt5: {e}")
        print()
        print("=" * 70)
        print("  RESULT: PyQt5 is NOT installed!")
        print("  Solution: Install PyQt5")
        print("    pip install PyQt5==5.15.9")
        print("=" * 70)
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    print()
    input("Press Enter to exit...")
