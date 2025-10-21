# How to Check if WinUSB Driver is Installed (Windows)

## Method 1: Using Device Manager

1. **Open Device Manager**
   - Press `Win + X` and select "Device Manager"
   - Or press `Win + R`, type `devmgmt.msc`, and press Enter

2. **Locate your thermal camera**
   - Look under these sections:
     - **"Universal Serial Bus devices"** - If WinUSB is installed, you'll see it here
     - **"Cameras"** or **"Imaging devices"**
     - **"Other devices"** - If driver is missing, it appears here with a yellow exclamation mark
     - **"libusb-win32 devices"** or **"WinUSB devices"**

3. **Check the driver details**
   - Right-click on the device (look for VID_0BDA&PID_5840 in the hardware ID)
   - Select **"Properties"**
   - Go to the **"Driver"** tab
   - Check **"Driver Provider"**:
     - ✅ **"Microsoft"** = WinUSB driver is installed correctly
     - ❌ **Other provider or missing** = WinUSB not installed

4. **Verify Hardware IDs**
   - In Properties, go to **"Details"** tab
   - Select **"Hardware IDs"** from the dropdown
   - Look for: `USB\VID_0BDA&PID_5840`

## Method 2: Using PowerShell (Quick Check)

```powershell
# Run PowerShell as Administrator
Get-PnpDevice | Where-Object {$_.InstanceId -like "*VID_0BDA&PID_5840*"} | Format-List FriendlyName, InstanceId, Status, Class, Service

# Look for:
# - Service: WinUSB (indicates WinUSB driver)
# - Status: OK (device is working)
# - Class: USBDevice or similar
```

## Method 3: Using Registry (Advanced)

```powershell
# Check registry for WinUSB driver
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Enum\USB\VID_0BDA&PID_5840\*" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Service
```

If it returns **"WinUSB"**, the driver is installed.

## Method 4: Using Python Script

Run this script to check programmatically:

```python
import subprocess
import re

print("Checking for thermal camera and WinUSB driver...\n")

# Query USB devices
cmd = ['powershell', '-Command',
       "Get-PnpDevice | Where-Object {$_.InstanceId -like '*VID_0BDA&PID_5840*'} | " +
       "Select-Object FriendlyName, InstanceId, Status, Class, Service, DriverProvider | Format-List"]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout.strip():
        print("✓ Camera device found!")
        print(result.stdout)

        # Check if WinUSB is mentioned
        if 'WinUSB' in result.stdout or 'winusb' in result.stdout.lower():
            print("\n✅ WinUSB driver appears to be installed")
        elif 'Microsoft' in result.stdout:
            print("\n✅ Microsoft driver installed (likely WinUSB)")
        else:
            print("\n⚠️  WinUSB driver may NOT be installed")
            print("   Check the 'Service' and 'DriverProvider' fields above")
    else:
        print("❌ Camera device NOT found (VID_0BDA&PID_5840)")
        print("   Make sure camera is plugged in")

except Exception as e:
    print(f"Error checking device: {e}")
```

## What You Should See

### ✅ WinUSB Driver Installed Correctly
```
FriendlyName    : AC010_256 Thermal Camera (or similar)
Status          : OK
DriverProvider  : Microsoft
Service         : WinUSB
```

### ❌ WinUSB Driver NOT Installed
```
FriendlyName    : Unknown Device
Status          : Error
DriverProvider  : (None) or (Other)
Service         : (None)
```

Or the device appears under **"Other devices"** with a yellow exclamation mark.

## If WinUSB is NOT Installed

### Install using Zadig:

1. **Download Zadig**: https://zadig.akeo.ie/
2. **Run Zadig** (no installation needed)
3. **Options → List All Devices** (check this option)
4. **Select your thermal camera** from the dropdown
   - Look for VID: 0BDA, PID: 5840
5. **Select "WinUSB"** from the driver dropdown (green arrow area)
6. **Click "Install Driver"** or **"Replace Driver"**
7. **Wait** for installation to complete
8. **Unplug and replug** the camera

### Verify Installation
After installing with Zadig, go back to Device Manager and verify:
- Device appears under "Universal Serial Bus devices"
- Driver Provider shows "Microsoft"
- No yellow exclamation marks

## Troubleshooting

**Device not visible in Zadig?**
- Make sure camera is plugged in
- Check "Options → List All Devices" in Zadig
- Try a different USB port

**Installation fails?**
- Run Zadig as Administrator (right-click → Run as administrator)
- Disable driver signature enforcement temporarily (advanced)

**Multiple entries for same device?**
- This is normal if you've plugged it into different ports
- Install WinUSB for all instances, or just the current one
