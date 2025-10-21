#!/usr/bin/env python3
"""
WinUSB Driver Installation Tool for Thermal Camera

Automates driver installation using Zadig on Windows.
"""

import sys
import os
import subprocess
import urllib.request
import tempfile

def is_admin():
    """Check if running with administrator privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the script with administrator privileges"""
    import ctypes
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])

    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        return True
    except:
        return False

def check_device_status():
    """Check if camera is present and what driver it has"""
    print("Checking for thermal camera...")

    cmd = [
        'powershell', '-Command',
        "Get-PnpDevice | Where-Object {$_.InstanceId -like '*VID_0BDA&PID_5840*'} | " +
        "Select-Object FriendlyName, Status, Service"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print(f"\n{result.stdout}")

            if 'winusb' in result.stdout.lower():
                return 'winusb_installed'
            elif result.stdout.strip():
                return 'other_driver'
            else:
                return 'no_driver'
        else:
            return 'not_found'
    except Exception as e:
        print(f"Error checking device: {e}")
        return 'error'

def download_zadig():
    """Download Zadig tool"""
    zadig_url = "https://github.com/pbatard/libwdi/releases/download/v1.5.0/zadig-2.8.exe"
    temp_dir = tempfile.gettempdir()
    zadig_path = os.path.join(temp_dir, "zadig.exe")

    if os.path.exists(zadig_path):
        print(f"✓ Zadig already downloaded: {zadig_path}")
        return zadig_path

    print(f"Downloading Zadig from: {zadig_url}")
    try:
        urllib.request.urlretrieve(zadig_url, zadig_path)
        print(f"✓ Downloaded to: {zadig_path}")
        return zadig_path
    except Exception as e:
        print(f"✗ Failed to download: {e}")
        print("\nPlease download manually from: https://zadig.akeo.ie/")
        return None

def install_driver():
    """Guide user through driver installation"""
    print("\n" + "="*70)
    print("  WinUSB Driver Installation")
    print("="*70)

    # Download Zadig
    zadig_path = download_zadig()
    if not zadig_path:
        return False

    # Instructions
    print("\n📋 INSTALLATION STEPS:")
    print("\nWhen Zadig opens, follow these steps:")
    print("\n  1. Click 'Options' → Check 'List All Devices'")
    print("  2. From the dropdown, select 'Tiny1C'")
    print("     (or device showing VID_0BDA PID_5840)")
    print("  3. In the driver area (green arrow →), ensure 'WinUSB' is selected")
    print("  4. Click 'Install Driver' or 'Replace Driver'")
    print("  5. Wait for installation to complete (1-2 minutes)")
    print("  6. Close Zadig when done")
    print("\n" + "="*70)

    input("\nPress Enter to launch Zadig...")

    # Launch Zadig
    try:
        subprocess.Popen([zadig_path])
        print("\n✓ Zadig launched")
        print("\nFollow the steps above in Zadig...")
        input("\nPress Enter when driver installation is complete...")
        return True
    except Exception as e:
        print(f"\n✗ Failed to launch Zadig: {e}")
        return False

def verify_installation():
    """Verify WinUSB driver is installed"""
    print("\n" + "="*70)
    print("  Verifying Installation")
    print("="*70)

    cmd = [
        'powershell', '-Command',
        "Get-PnpDevice | Where-Object {$_.InstanceId -like '*VID_0BDA&PID_5840*'} | " +
        "Select-Object FriendlyName, Status, Service, DriverProvider | Format-List"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print(result.stdout)

            if 'winusb' in result.stdout.lower() and 'ok' in result.stdout.lower():
                print("="*70)
                print("  ✅ SUCCESS! WinUSB driver is installed correctly!")
                print("="*70)
                print("\n📝 Next steps:")
                print("  1. Unplug camera, wait 5 seconds, plug back in")
                print("  2. Test with: python tools/troubleshoot.py")
                print("  3. Or run: python tests/test_simple.py")
                return True
            else:
                print("\n⚠️  Driver may not be installed correctly")
                print("   Expected: Service = WinUSB")
                print("   Try running this script again")
                return False
        else:
            print("\n❌ Camera not detected")
            print("   Make sure camera is plugged in")
            return False
    except Exception as e:
        print(f"\n❌ Error verifying: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        WinUSB Driver Installation Tool                               ║
║        For Tiny1C / AC010_256 Thermal Camera                         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    if sys.platform != 'win32':
        print("❌ This tool is for Windows only.")
        print("   On Linux, use udev rules (see README.md)")
        return 1

    # Check admin privileges
    if not is_admin():
        print("⚠️  Administrator privileges required")
        print("   Attempting to restart with elevated privileges...")
        if run_as_admin():
            return 0
        else:
            print("\n❌ Failed to elevate privileges")
            print("\nPlease run this script as Administrator:")
            print("  Right-click → Run as Administrator")
            return 1

    print("✓ Running with Administrator privileges\n")

    # Check device status
    device_status = check_device_status()

    if device_status == 'not_found':
        print("\n" + "="*70)
        print("  ❌ Camera Not Detected")
        print("="*70)
        print("\nThe thermal camera was not detected.")
        print("\n📋 Checklist:")
        print("  □ Camera is plugged into USB port")
        print("  □ Camera power LED is on (if applicable)")
        print("  □ USB cable is functional (try different port/cable)")
        print("\nPlug in the camera and run this script again.")
        return 1

    elif device_status == 'winusb_installed':
        print("\n" + "="*70)
        print("  ✅ WinUSB Driver Already Installed!")
        print("="*70)
        print("\nYour camera is already configured correctly.")
        print("\nIf you're still having issues:")
        print("  1. Unplug camera, wait 5 seconds, plug back in")
        print("  2. Run: python tools/troubleshoot.py")
        return 0

    elif device_status == 'other_driver':
        print("\n" + "="*70)
        print("  ⚠️  Camera Found - Driver Needs Replacement")
        print("="*70)
        print("\nYour camera is using a different driver (probably libusbK).")
        print("We need to replace it with WinUSB.")
        print()

    elif device_status == 'no_driver':
        print("\n" + "="*70)
        print("  ⚠️  Camera Found - Driver Not Installed")
        print("="*70)
        print("\nYour camera needs the WinUSB driver installed.")
        print()

    # Offer to install
    choice = input("Proceed with driver installation? (y/n): ").strip().lower()
    if choice != 'y':
        print("\nInstallation cancelled.")
        return 0

    # Install driver
    if install_driver():
        # Verify
        print("\nVerifying installation...")
        if verify_installation():
            return 0
        else:
            print("\n⚠️  Verification failed. You may need to:")
            print("  1. Unplug and replug the camera")
            print("  2. Restart Windows")
            print("  3. Try the installation again")
            return 1
    else:
        print("\n❌ Installation failed or was cancelled")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print("\n" + "="*70)
        input("Press Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
