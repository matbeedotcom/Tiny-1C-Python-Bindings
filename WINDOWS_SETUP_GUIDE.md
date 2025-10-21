# Windows Setup Guide - Thermal Camera

**Goal**: Make it as easy as possible for Windows users to get the thermal camera working.

## 🚀 Quick Start (Recommended)

### Option 1: Automated Setup (Easiest)

Just run the setup script - it handles everything:

```batch
SETUP_WINDOWS.bat
```

This will:
1. ✅ Check Python installation
2. ✅ Build the package (if needed)
3. ✅ Check for the camera
4. ✅ Install WinUSB driver (guided)
5. ✅ Test the camera

**That's it!** The script guides you through everything.

---

## 📋 Manual Setup (If needed)

### Step 1: Build the Package

```batch
# Build using the provided script
build_windows.bat

# OR manually
python setup_crossplatform.py build_ext --inplace
```

### Step 2: Check Driver Status

```batch
python check_driver.py
```

This tells you:
- ✅ If WinUSB is installed
- ⚠️ If you need to install it
- ❌ If the camera isn't detected

### Step 3: Install WinUSB Driver

**Automated (Recommended)**:
```batch
python install_driver.py
```

**Manual**:
1. Download [Zadig](https://zadig.akeo.ie/)
2. Run as Administrator
3. Options → List All Devices
4. Select "Tiny1C" (VID_0BDA, PID_5840)
5. Choose "WinUSB" as target driver
6. Click "Replace Driver"

### Step 4: Test Camera

```batch
python diagnose_camera.py
```

This runs comprehensive diagnostics and tells you if everything is working.

---

## 🔧 Troubleshooting

### Problem: "Camera not detected"

**Solutions**:
1. Check USB connection (try different port)
2. Verify camera LED is on
3. Try different USB cable
4. Check Device Manager for unknown devices

### Problem: "Failed to open camera"

**Most likely cause**: Wrong driver installed

**Check current driver**:
```batch
python check_driver.py
```

**Solution**: Install WinUSB driver
```batch
python install_driver.py
```

### Problem: "Package not found / Import error"

**Solution**: Build the package first
```batch
build_windows.bat
```

### Problem: "DLL load failed"

**Solutions**:
1. Rebuild from clean state:
   ```batch
   python setup.py clean --all
   build_windows.bat
   ```

2. Check that DLLs are in the right location:
   ```
   libs/win/x64/dll/
   ```

---

## 📊 Understanding Windows Drivers

### Why WinUSB?

The thermal camera SDK (`libiruvc`) is compiled to use **WinUSB** on Windows. This is Microsoft's standard USB driver.

### What if I have libusbK?

libusbK is another libusb-compatible driver, but the SDK specifically needs WinUSB. You must **replace** libusbK with WinUSB using Zadig.

### Driver Comparison

| Driver | Compatible? | How to Install |
|--------|-------------|----------------|
| **WinUSB** | ✅ YES | Zadig (recommended) |
| libusbK | ❌ NO | Replace with WinUSB |
| libusb-win32 | ❌ NO | Replace with WinUSB |
| Generic USB | ❌ NO | Install WinUSB |

---

## 🎯 For Developers: Reducing Driver Hassle

### Current Limitations

The camera SDK requires a specific USB backend (WinUSB). This requires users to:
1. Know about driver installation
2. Download and use Zadig
3. Select the correct driver

### Potential Solutions (Future)

#### 1. **Bundle Driver Package** (Best for enterprise)
- Create signed `.inf` + `.cat` files
- Distribute with installer
- Automated installation via PnPUtil
- **Requires**: Code signing certificate ($$$)

#### 2. **Use libusb-1.0 Generic Backend** (Best for open source)
- Modify SDK to use generic libusb-1.0
- Works with WinUSB, libusbK, libusb-win32
- No driver switching needed
- **Requires**: SDK source code access

#### 3. **Windows Store Packaging** (Best for consumers)
- Publish as Windows Store app
- Drivers auto-installed
- **Requires**: Microsoft Store developer account

#### 4. **Script-Based Automation** (Current approach)
- Download Zadig automatically
- Guide user through process
- Minimize manual steps
- **Advantage**: No code signing needed

### Why We Can't Fully Automate

Windows requires **administrator privileges** and **user consent** for driver installation. This is a security feature. We can:
- ✅ Download Zadig
- ✅ Launch it
- ✅ Guide the user
- ❌ Click the buttons for them (security restriction)

Tools like AutoHotKey could automate clicks, but that's fragile and not recommended.

---

## 📁 Setup Scripts Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `SETUP_WINDOWS.bat` | Complete first-time setup | First time setup |
| `check_driver.py` | Check WinUSB driver status | Verify driver |
| `install_driver.py` | Install WinUSB driver | Driver installation |
| `diagnose_camera.py` | Full diagnostic test | Troubleshooting |
| `setup_camera.py` | Interactive setup wizard | Guided setup |

---

## ✅ Checklist for Users

Before reporting issues, please verify:

- [ ] Python is installed (3.8+)
- [ ] Package is built (`build_windows.bat`)
- [ ] Camera is plugged in and powered on
- [ ] WinUSB driver is installed (`python check_driver.py`)
- [ ] No other app is using the camera
- [ ] Ran diagnostic test (`python diagnose_camera.py`)

---

## 🆘 Getting Help

If you're still having issues:

1. **Run diagnostics**:
   ```batch
   python diagnose_camera.py > diagnostic_output.txt
   ```

2. **Check driver**:
   ```batch
   python check_driver.py > driver_status.txt
   ```

3. **Open Device Manager**:
   - Take screenshot of USB devices
   - Look for Tiny1C or unknown devices

4. **Create issue** with:
   - `diagnostic_output.txt`
   - `driver_status.txt`
   - Device Manager screenshot
   - Your Windows version

---

## 🎉 Success Indicators

You know it's working when:

✅ `python check_driver.py` shows "WinUSB driver is INSTALLED"

✅ `python diagnose_camera.py` completes all checks

✅ This code works:
```python
import tiny_thermal_camera

with tiny_thermal_camera.ThermalCamera() as camera:
    camera.start_stream()
    temp_frame, _ = camera.capture_frame()
    print(f"Got temperature data: {temp_frame.shape}")
```

---

## 📚 Additional Resources

- [Zadig Official Site](https://zadig.akeo.ie/)
- [WinUSB Documentation](https://docs.microsoft.com/en-us/windows-hardware/drivers/usbcon/winusb)
- [libusb Windows](https://github.com/libusb/libusb/wiki/Windows)
