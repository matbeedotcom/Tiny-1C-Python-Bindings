# 🚀 Thermal Camera Quick Reference Card

## First Time Setup (Windows)

```batch
setup.bat
```

That's it! The wizard handles everything.

---

## Useful Commands

| Command | Purpose |
|---------|---------|
| `setup.bat` | Complete first-time setup |
| `python tools/troubleshoot.py` | All-in-one troubleshooting tool |
| `python tools/install_driver.py` | Install WinUSB driver |
| `build_windows.bat` | Build the package |

---

## Quick Test

```python
import tiny_thermal_camera

with tiny_thermal_camera.ThermalCamera() as camera:
    camera.start_stream()
    temp_frame, _ = camera.capture_frame()

    if temp_frame is not None:
        print("✅ Camera working!")
        stats = camera.get_temperature_stats(temp_frame)
        print(f"Temp range: {stats['min']:.1f}°C - {stats['max']:.1f}°C")
    else:
        print("❌ No frame captured")
```

---

## Common Issues

### "Failed to open camera"
→ **Solution**: Install WinUSB driver
```batch
python install_driver.py
```

### "Camera not detected"
→ **Check**:
- Camera plugged in
- USB cable working
- Try different USB port

### "Import error"
→ **Solution**: Build package
```batch
build_windows.bat
```

---

## Driver Installation (Manual)

1. Download Zadig: https://zadig.akeo.ie/
2. Run as Administrator
3. Options → List All Devices
4. Select "Tiny1C"
5. Choose "WinUSB"
6. Click "Replace Driver"

---

## Basic Usage

```python
import tiny_thermal_camera

# Create camera
camera = tiny_thermal_camera.ThermalCamera()

# Initialize and open
camera.initialize()
camera.open()

# Start streaming
camera.start_stream()

# Get frame
temp_frame = camera.get_raw_frame()

# Convert to Celsius
temp_celsius = tiny_thermal_camera.temp_to_celsius(temp_frame[96, 128])

# Cleanup
camera.stop_stream()
camera.close()
```

---

## Camera Info

- **Resolution**: 256×192 pixels
- **VID**: 0x0BDA
- **PID**: 0x5840
- **Driver**: WinUSB (required)

---

## Help

Full documentation: `README.md`
Windows guide: `WINDOWS_SETUP_GUIDE.md`
Driver help: `check_winusb_driver.md`

---

**Print this page for quick reference!**
