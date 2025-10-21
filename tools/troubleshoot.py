#!/usr/bin/env python3
"""
All-in-One Thermal Camera Troubleshooting Tool

This script helps diagnose and fix camera issues, generate bug reports,
and guide users through common problems.
"""

import sys
import os
import platform
import subprocess
import webbrowser

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_menu(title, options):
    """Print a menu and get user choice"""
    print_header(title)
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print(f"  {len(options) + 1}. Exit")
    print()
    choice = input("Select option: ").strip()
    try:
        choice_num = int(choice)
        if 1 <= choice_num <= len(options):
            return choice_num
        elif choice_num == len(options) + 1:
            return 0  # Exit
    except ValueError:
        pass
    return -1  # Invalid

def check_python_environment():
    """Check Python version and environment"""
    print_header("Python Environment")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Executable: {sys.executable}")

def check_package_installed():
    """Check if tiny_thermal_camera is installed"""
    print_header("Checking Package Installation")
    try:
        import tiny_thermal_camera
        print("✅ Package 'tiny_thermal_camera' is installed")
        return True
    except ImportError as e:
        print("❌ Package 'tiny_thermal_camera' is NOT installed")
        print(f"\nError: {e}")
        print("\nTo install:")
        print("  Option 1: pip install tiny-thermal-camera")
        print("  Option 2: python setup_crossplatform.py build_ext --inplace")
        if sys.platform == 'win32':
            print("  Option 3: build_windows.bat")
        return False

def check_driver_status_windows():
    """Check Windows driver status"""
    print_header("Checking WinUSB Driver (Windows)")

    cmd = [
        'powershell', '-Command',
        "Get-PnpDevice | Where-Object {$_.InstanceId -like '*VID_0BDA&PID_5840*'} | " +
        "Select-Object FriendlyName, Status, Service, DriverProvider | Format-List"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

        if result.returncode == 0 and result.stdout.strip():
            print("Device Information:")
            print("-" * 70)
            print(result.stdout)
            print("-" * 70)

            output_lower = result.stdout.lower()

            if 'winusb' in output_lower and 'ok' in output_lower:
                print("\n✅ WinUSB driver is installed and device is OK")
                return 'installed'
            elif 'ok' in output_lower:
                current_driver = 'libusbK' if 'libusb' in output_lower else 'unknown'
                print(f"\n⚠️ Device OK but using '{current_driver}' driver (need WinUSB)")
                return 'wrong_driver'
            else:
                print("\n❌ Device found but not working properly")
                return 'device_error'
        else:
            print("❌ Camera NOT detected")
            print("\nPossible reasons:")
            print("  - Camera not plugged in")
            print("  - Camera not powered on")
            print("  - USB cable faulty")
            print("  - USB port not working")
            return 'not_found'

    except Exception as e:
        print(f"❌ Error checking driver: {e}")
        return 'error'

def test_camera_basic():
    """Run basic camera test"""
    print_header("Testing Camera Connection")

    try:
        import tiny_thermal_camera

        camera = tiny_thermal_camera.ThermalCamera()

        print("Step 1: Initializing camera system...")
        if not camera.initialize():
            print("  ❌ FAILED: Camera system initialization failed")
            print("\n  This indicates a USB library issue")
            return False
        print("  ✅ Camera system initialized")

        print("\nStep 2: Getting device list...")
        success, devices = camera.get_device_list()
        if not success:
            print("  ❌ FAILED: Cannot enumerate USB devices")
            return False

        print(f"  ✅ Found {len(devices)} USB device(s)")
        for i, dev in enumerate(devices):
            print(f"     Device {i}: VID=0x{dev['vid']:04X}, PID=0x{dev['pid']:04X}, Name='{dev['name']}'")

        # Check for thermal camera
        target_found = any(d['vid'] == 0x0BDA and d['pid'] == 0x5840 for d in devices)
        if not target_found:
            print("\n  ⚠️ WARNING: Thermal camera (VID=0x0BDA, PID=0x5840) not in list")
            print("     Camera may not be detected by the OS")
            return False

        print("\nStep 3: Opening camera...")
        if not camera.open():
            print("  ❌ FAILED: Cannot open camera")
            print("\n  Most likely cause: Driver issue (WinUSB not installed)")
            return False

        print("  ✅ Camera opened successfully!")

        camera.close()
        print("\n✅ ALL TESTS PASSED - Camera is working correctly!")
        return True

    except Exception as e:
        print(f"\n  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_bug_report():
    """Generate comprehensive bug report"""
    print_header("Generating Bug Report")

    report_lines = []
    report_lines.append("# Thermal Camera Bug Report\n")
    report_lines.append(f"Generated: {platform.platform()}\n")
    report_lines.append(f"Python: {sys.version}\n\n")

    # System info
    report_lines.append("## System Information\n")
    report_lines.append(f"- OS: {platform.platform()}\n")
    report_lines.append(f"- Python: {sys.version}\n")
    report_lines.append(f"- Architecture: {platform.machine()}\n\n")

    # Package status
    report_lines.append("## Package Status\n")
    try:
        import tiny_thermal_camera
        report_lines.append("- Package: INSTALLED ✅\n\n")
    except ImportError as e:
        report_lines.append(f"- Package: NOT INSTALLED ❌\n")
        report_lines.append(f"- Error: {e}\n\n")

    # Driver status (Windows)
    if sys.platform == 'win32':
        report_lines.append("## Driver Status (Windows)\n")
        cmd = ['powershell', '-Command',
               "Get-PnpDevice | Where-Object {$_.InstanceId -like '*VID_0BDA&PID_5840*'} | " +
               "Select-Object FriendlyName, Status, Service, DriverProvider | Format-List"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.stdout.strip():
                report_lines.append("```\n")
                report_lines.append(result.stdout)
                report_lines.append("```\n\n")
            else:
                report_lines.append("- Camera: NOT DETECTED ❌\n\n")
        except:
            report_lines.append("- Error checking driver status\n\n")

    # Camera test
    report_lines.append("## Camera Test Results\n")
    print("\nRunning camera tests...")
    try:
        import tiny_thermal_camera
        camera = tiny_thermal_camera.ThermalCamera()

        if camera.initialize():
            report_lines.append("- Initialize: SUCCESS ✅\n")
            success, devices = camera.get_device_list()
            if success:
                report_lines.append(f"- Device List: {len(devices)} device(s) ✅\n")
                for d in devices:
                    report_lines.append(f"  - VID=0x{d['vid']:04X}, PID=0x{d['pid']:04X}\n")
            else:
                report_lines.append("- Device List: FAILED ❌\n")

            if camera.open():
                report_lines.append("- Open Camera: SUCCESS ✅\n")
                camera.close()
            else:
                report_lines.append("- Open Camera: FAILED ❌\n")
        else:
            report_lines.append("- Initialize: FAILED ❌\n")
    except Exception as e:
        report_lines.append(f"- Test Error: {e}\n")

    report_lines.append("\n## Additional Information\n")
    report_lines.append("(Add any additional details about your issue here)\n\n")

    # Save report
    report_file = "thermal_camera_bug_report.txt"
    with open(report_file, 'w') as f:
        f.writelines(report_lines)

    print(f"\n✅ Bug report saved to: {report_file}")
    print("\nReport contents:")
    print("=" * 70)
    print(''.join(report_lines))
    print("=" * 70)

    return report_file

def open_github_issues():
    """Open GitHub issues page"""
    # Update with your actual GitHub URL
    github_url = "https://github.com/yourusername/Tiny-1C-Python-Bindings/issues/new"
    print(f"\nOpening GitHub issues page: {github_url}")
    print("\nPlease attach the bug report file when creating your issue.")
    try:
        webbrowser.open(github_url)
    except:
        print(f"\nCouldn't open browser automatically. Please visit:\n{github_url}")

def run_driver_installer():
    """Launch driver installation script"""
    print_header("Driver Installation")

    install_script = os.path.join(os.path.dirname(__file__), 'install_driver.py')

    if os.path.exists(install_script):
        print(f"Launching driver installer...\n")
        try:
            subprocess.run([sys.executable, install_script])
        except Exception as e:
            print(f"Error running installer: {e}")
    else:
        print(f"❌ Driver installer not found at: {install_script}")
        print("\nManual installation:")
        print("1. Download Zadig: https://zadig.akeo.ie/")
        print("2. Run as Administrator")
        print("3. Options → List All Devices")
        print("4. Select 'Tiny1C' (VID_0BDA, PID_5840)")
        print("5. Choose 'WinUSB' as driver")
        print("6. Click 'Replace Driver'")

def main_menu():
    """Main troubleshooting menu"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        Thermal Camera Troubleshooting Tool                           ║
║        Tiny1C / AC010_256 Series                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

This tool helps diagnose and fix camera issues.
""")

    while True:
        choice = print_menu(
            "Main Menu",
            [
                "Quick Diagnostics (Recommended)",
                "Check Driver Status (Windows)",
                "Test Camera Connection",
                "Install/Fix WinUSB Driver",
                "Generate Bug Report",
                "Open GitHub Issues Page"
            ]
        )

        if choice == 0:  # Exit
            print("\nGoodbye!")
            break
        elif choice == 1:  # Quick Diagnostics
            check_python_environment()
            pkg_ok = check_package_installed()
            if not pkg_ok:
                print("\n⚠️ Cannot continue diagnostics without package installed")
                continue

            if sys.platform == 'win32':
                driver_status = check_driver_status_windows()
                if driver_status in ['wrong_driver', 'device_error', 'not_found']:
                    print("\n💡 TIP: Try option 4 to install/fix the WinUSB driver")

            test_camera_basic()

        elif choice == 2:  # Check Driver
            if sys.platform != 'win32':
                print("\n⚠️ Driver check is Windows-specific (not needed on Linux)")
            else:
                check_driver_status_windows()

        elif choice == 3:  # Test Camera
            if not check_package_installed():
                continue
            test_camera_basic()

        elif choice == 4:  # Install Driver
            if sys.platform != 'win32':
                print("\n⚠️ Driver installation is Windows-specific")
            else:
                run_driver_installer()

        elif choice == 5:  # Bug Report
            report_file = generate_bug_report()
            print(f"\n📝 Next steps:")
            print(f"   1. Review the report: {report_file}")
            print(f"   2. Add any additional details")
            print(f"   3. Create a GitHub issue (option 6)")
            print(f"   4. Attach the report file")

        elif choice == 6:  # GitHub Issues
            open_github_issues()

        else:
            print("\n❌ Invalid option, please try again")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
