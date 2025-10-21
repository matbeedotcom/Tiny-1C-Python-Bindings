# Tiny Thermal Camera Python Bindings

Cross-platform Python bindings for the AC010_256 thermal camera SDK, supporting P2/Tiny1C thermal cameras on Windows, Linux (x86, ARM, MIPS), and macOS.

## Features

- **Cross-Platform Support**: Windows, Linux (x86, ARM, MIPS), and macOS
- **Camera Control**: Open/close camera, start/stop streaming
- **Temperature Measurement**: Point, line, and area temperature analysis  
- **Real-time Data**: Get temperature and image frames as NumPy arrays
- **Easy Integration**: Simple Python API with context manager support
- **Self-Contained**: Automatic DLL/library management - no manual setup required
- **Architecture Support**: Multiple ARM and MIPS variants for embedded systems
- **Comprehensive Examples**: Demo scripts and utilities included

## Installation

### 🚀 Quick Start (Windows Users)

**NEW: Automated Setup Script!**

```batch
# Run the automated setup wizard (from project root)
setup.bat
```

This handles **everything**:
- ✅ Builds the package
- ✅ Checks for camera
- ✅ Installs WinUSB driver (guided)
- ✅ Tests your setup

**See [WINDOWS_SETUP_GUIDE.md](WINDOWS_SETUP_GUIDE.md) for detailed Windows instructions.**

**All setup tools:** [tools/README.md](tools/README.md)

---

### Simple Installation (Recommended)

```bash
# Install pre-compiled wheel from PyPI
pip install tiny-thermal-camera
```

**Pre-compiled wheels available for:**
- **Windows**: Python 3.8-3.12 (x64) - **No build tools required!**
- **Linux**: Python 3.8-3.12 (x86_64, aarch64)

**Benefits:**
- No C++ compiler or build tools needed
- Instant installation
- All libraries bundled automatically
- Works out of the box

**Note for Windows users**: You still need to install the WinUSB driver - see the Quick Start section above.

### Alternative: Install from Source

```bash
# Install from source (requires build tools)
pip install .
```

**Note:** Building from source requires:
- **Windows**: [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) - See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)
- **Linux**: GCC, Python development headers

**After installation, the package automatically:**
- Detects your platform (Windows/Linux/macOS) and architecture (x86/ARM/MIPS)
- Includes all necessary libraries and DLLs
- Sets up runtime library loading
- No manual library management required!

### Platform-Specific Notes

#### Windows
- **Pre-compiled wheels available** - no build tools needed!
- All required DLLs are automatically included and loaded
- No additional Visual C++ Redistributable installation needed
- For build-from-source instructions, see [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)

#### Linux
- Static library linking used by default (no runtime dependencies)
- Supports x86, ARM (various variants), and MIPS architectures
- Cross-compilation supported via environment variables

#### Cross-Compilation (Advanced)
```bash
# Example: Cross-compile for ARM
export CROSS_COMPILE=arm-linux-gnueabihf
export TARGET_ARCH=arm
pip install .
```

### Development Installation

```bash
# Development install with editable mode
pip install -e .

# Build in-place for development
python setup.py build_ext --inplace
```

## Usage

### Quick Start

```python
import tiny_thermal_camera

# Context manager automatically handles initialization, open, and cleanup
with tiny_thermal_camera.ThermalCamera() as camera:
    # Start streaming (waits 5s for P2 series stabilization)
    if camera.start_streaming():
        # Capture a frame
        temp_frame, image_frame = camera.capture_frame()
        
        if temp_frame is not None:
            # Get temperature statistics
            stats = camera.get_temperature_stats(temp_frame)
            print(f"Temperature range: {stats['min']:.1f}°C - {stats['max']:.1f}°C")
            
            # Find hottest point
            hot_pos, hot_temp = camera.find_hotspot(temp_frame)
            print(f"Hotspot: {hot_temp:.1f}°C at position {hot_pos}")
```

### Advanced Usage (Manual Resource Management)

```python
import tiny_thermal_camera
import numpy as np

# Direct API access with manual resource management
camera = tiny_thermal_camera.ThermalCamera()
# Note: TemperatureProcessor is a static class, don't instantiate

try:
    # Manual initialization and open
    camera.initialize()
    if camera.open():
        camera.start_stream()
        
        # Get camera info
        width, height, fps = camera.get_camera_info()
        
        # Get raw temperature frame
        temp_frame = camera.get_raw_frame()
        
        # Point temperature
        success, temp = tiny_thermal_camera.TemperatureProcessor.get_point_temp(temp_frame, 128, 96)
        if success:
            print(f"Temperature at center: {temp:.1f}°C")
        
        # Area temperature
        success, max_t, min_t, avg_t = tiny_thermal_camera.TemperatureProcessor.get_rect_temp(
            temp_frame, 100, 80, 50, 50)
        if success:
            print(f"Area stats - Max: {max_t:.1f}°C, Min: {min_t:.1f}°C, Avg: {avg_t:.1f}°C")
finally:
    # Manual cleanup
    camera.close()
```

## Demo Scripts

### Interactive Demo

```bash
python3 thermal_camera_demo.py
```

Features:
- Camera initialization and streaming
- Single frame capture and analysis
- Temperature visualization with matplotlib/OpenCV
- Continuous monitoring mode
- Point, line, and area temperature measurement

### Simple Tests

```bash
# Basic functionality test
python3 test_simple.py

# Continuous monitoring
python3 test_continuous.py

# Context manager test
python3 test.py

# Context manager persistence test
python3 test_context_persistence.py
```

## API Reference

### tiny_thermal_camera.ThermalCamera Class

#### Context Manager Support
```python
import tiny_thermal_camera

# Context manager handles initialization and opening
with tiny_thermal_camera.ThermalCamera() as camera:
    # Camera is initialized and opened
    camera.start_streaming()  # User controls streaming

# Camera and stream remain active after context manager exits!
# This allows for continuous monitoring beyond the 'with' block
temp_frame, _ = camera.capture_frame()  # Still works!

# User explicitly controls cleanup when ready
camera.stop_stream()
camera.close()
```

#### Core Methods
- `initialize()` - Initialize camera system
- `open(vid=0x0BDA, pid=0x5840)` - Open the thermal camera
- `close()` - Close the camera
- `start_stream(enable_temperature_mode=True, wait_seconds=5)` - Start streaming with temperature mode
- `start_streaming(enable_temperature_mode=True, wait_seconds=5)` - Alias for start_stream
- `stop_stream()` - Stop streaming
- `get_camera_info()` - Get (width, height, fps)
- `get_raw_frame()` - Get raw temperature data as uint16 numpy array
- `get_device_list()` - Get available USB devices
- `is_open()` - Check if camera is open
- `is_streaming()` - Check if streaming

#### Convenience Methods
- `capture_frame()` - Get (temp_frame, image_frame) tuple
- `get_temperature_stats(temp_frame)` - Get comprehensive statistics dict
- `find_hotspot(temp_frame)` - Find hottest point and temperature

### tiny_thermal_camera.TemperatureProcessor Class

#### Static Methods
- `tiny_thermal_camera.temp_to_celsius(raw_value)` - Convert raw temperature to Celsius
- `TemperatureProcessor.get_point_temp(frame, x, y)` - Get temperature at point
- `TemperatureProcessor.get_rect_temp(frame, x, y, w, h)` - Get area temperature stats
- `TemperatureProcessor.get_line_temp(frame, x1, y1, x2, y2)` - Get line temperature stats

### Usage Examples

#### Simple Temperature Reading
```python
import tiny_thermal_camera

with tiny_thermal_camera.ThermalCamera() as camera:
    if camera.start_streaming():
        temp_frame, _ = camera.capture_frame()
        if temp_frame is not None:
            stats = camera.get_temperature_stats(temp_frame)
            print(f"Average temperature: {stats['mean']:.1f}°C")
```

#### Finding Hot and Cold Spots
```python
import tiny_thermal_camera

with tiny_thermal_camera.ThermalCamera() as camera:
    if camera.start_streaming():
        temp_frame, _ = camera.capture_frame()
        if temp_frame is not None:
            hot_pos, hot_temp = camera.find_hotspot(temp_frame)
            print(f"Hottest point: {hot_temp:.1f}°C at {hot_pos}")
```

#### Continuous Temperature Monitoring
```python
import tiny_thermal_camera
import time

# Initialize camera with context manager
with tiny_thermal_camera.ThermalCamera() as camera:
    camera.start_streaming()

# Stream persists beyond context manager - continuous monitoring
print("Starting continuous temperature monitoring...")
print("Press Ctrl+C to stop")

try:
    frame_count = 0
    while True:
        temp_frame, _ = camera.capture_frame()
        if temp_frame is not None:
            frame_count += 1
            
            # Get temperature statistics
            stats = camera.get_temperature_stats(temp_frame)
            hot_pos, hot_temp = camera.find_hotspot(temp_frame)
            
            # Print status every 10 frames
            if frame_count % 10 == 0:
                print(f"Frame {frame_count}: "
                      f"Avg: {stats['mean']:.1f}°C, "
                      f"Range: {stats['min']:.1f}-{stats['max']:.1f}°C, "
                      f"Hotspot: {hot_temp:.1f}°C at {hot_pos}")
        
        time.sleep(0.1)  # ~10 FPS

except KeyboardInterrupt:
    print("\nStopping monitoring...")
finally:
    # Clean up when done
    camera.stop_stream()
    camera.close()
    print("Cleanup completed.")
```

## Troubleshooting

### 🔍 Quick Diagnostics

**First time setup or having issues? Use our automated tools:**

```batch
# Windows: Complete automated setup
setup.bat

# Having issues? Run the troubleshooter
python tools/troubleshoot.py
```

The troubleshooter is an all-in-one tool with interactive menus for:
- Quick diagnostics
- Driver checking/installation
- Camera testing
- Bug report generation

See [tools/README.md](tools/README.md) for complete tool documentation.

---

### Common Issues & Solutions

#### ❌ "Failed to open thermal camera"

**Most common cause:** WinUSB driver not installed or wrong driver in use

**Quick fix:**
```bash
# Check current driver status
python tools/check_driver.py

# If WinUSB not installed, run:
python tools/install_driver.py
```

**Manual fix:**
1. Download [Zadig](https://zadig.akeo.ie/)
2. Run Zadig as Administrator
3. Options → List All Devices
4. Select "Tiny1C" (VID_0BDA, PID_5840)
5. Choose "WinUSB" as target driver
6. Click "Replace Driver"
7. Unplug and replug camera

**Why this happens:**
- The camera SDK requires the **WinUSB** driver specifically
- You might have libusbK or another driver installed
- Windows doesn't automatically assign WinUSB to the device

---

#### ❌ "Camera not detected" / No devices found

**Checklist:**
```bash
# 1. Run diagnostics to see what's detected
python tools/diagnose_camera.py

# 2. Check USB connection
# - Try different USB port (preferably USB 3.0)
# - Try different USB cable
# - Check if camera LED is on

# 3. Check Device Manager (Windows)
# Win + X → Device Manager
# Look for:
# - Unknown devices
# - Yellow exclamation marks
# - Camera under "Universal Serial Bus devices"
```

**Common causes:**
- Camera not powered on
- Faulty USB cable
- USB port not working
- Driver not installed

---

#### ❌ Import Error: "No module named 'tiny_thermal_camera'"

**Solution:**
```bash
# If installing from PyPI
pip install tiny-thermal-camera

# If building from source
python setup.py build_ext --inplace
# or
build_windows.bat  # Windows
python setup_crossplatform.py build_ext --inplace  # Cross-platform
```

---

#### ❌ DLL Load Failed (Windows)

**Quick fix:**
```bash
# Clean rebuild
python setup.py clean --all
build_windows.bat

# Verify DLLs are present
dir libs\win\x64\dll\
```

**What to check:**
- All DLLs in `libs/win/x64/dll/` are present
- Using 64-bit Python (32-bit not supported)
- Visual C++ Redistributable installed

---

#### ❌ "Another application is using the camera"

**Solution:**
```bash
# Close other applications that might be using the camera
# Check Task Manager for:
# - Other Python processes
# - Camera applications
# - Video conferencing apps

# If still stuck, reboot and try again
```

---

#### ⚠️ Linux: Permission Denied

**Temporary fix:**
```bash
sudo chmod 666 /dev/bus/usb/*/*
```

**Permanent fix (udev rule):**
```bash
# Create udev rule
sudo nano /etc/udev/rules.d/99-thermal-camera.rules

# Add this line:
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="5840", MODE="0666"

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Unplug and replug camera
```

---

### 🛠️ Diagnostic Tools Reference

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `setup.bat` | Complete first-time setup | First time on new computer |
| `tools/troubleshoot.py` | All-in-one diagnostics & troubleshooting | Camera not working, need help |
| `tools/install_driver.py` | Install WinUSB driver | Driver installation needed |

**Full documentation:** [tools/README.md](tools/README.md)

---

### 📊 Understanding the Driver Requirement (Windows)

**Why do I need to install a driver?**

Your application includes all the necessary **DLLs** (software libraries), but Windows needs to know which **driver** to use for the USB hardware.

**What's the difference?**

| Component | Bundled? | Purpose |
|-----------|----------|---------|
| `libiruvc.dll` | ✅ YES | Camera SDK (included) |
| `libirtemp.dll` | ✅ YES | Processing (included) |
| `WinUSB driver` | ❌ NO | System USB driver (Windows has it) |
| **Driver Assignment** | ⚠️ **YOU CONFIGURE** | Tell Windows to use WinUSB for this device |

**The one-time setup:** Use Zadig to tell Windows "use WinUSB for this camera"

**This is normal!** Many USB devices require this (Arduino, STM32, logic analyzers, etc.)

**Good news:** Our automated tools make this easy!

---

### 🐛 Reporting Issues

If you've tried the above and still have problems:

1. **Run full diagnostics:**
   ```bash
   python tools/diagnose_camera.py > diagnostic_report.txt
   python tools/check_driver.py > driver_status.txt
   ```

2. **Gather information:**
   - Device Manager screenshot (Windows)
   - Your Python version: `python --version`
   - Your OS version
   - Output files from step 1

3. **Create an issue** with all the above information

---

### 📚 Additional Resources

- **Detailed Windows Guide:** [WINDOWS_SETUP_GUIDE.md](WINDOWS_SETUP_GUIDE.md)
- **Quick Reference:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Driver Check Guide:** [check_winusb_driver.md](check_winusb_driver.md)
- **Tools Documentation:** [tools/README.md](tools/README.md)

### Build Issues (Development)

#### Missing Dependencies
```bash
# Linux: Install build tools
sudo apt install build-essential python3-dev pkg-config

# Install from source
pip install . --verbose  # Shows detailed build output
```

#### Clean Rebuild
```bash
# Clean previous builds
python setup.py clean --all
pip install . --force-reinstall
```

### Runtime Issues
```python
# Test basic functionality
import tiny_thermal_camera

with tiny_thermal_camera.ThermalCamera() as camera:
    if camera.start_streaming():
        temp_frame, _ = camera.capture_frame()
        if temp_frame is not None:
            print("Camera working correctly!")
        else:
            print("Failed to capture frame")
    else:
        print("Failed to start streaming")
```

## Hardware Requirements

- **Compatible Cameras**: P2 series, Tiny1C, AC010_256
- **Connection**: USB interface (VID: 0x0BDA, PID: 0x5840)
- **Operating Systems**: 
  - Windows (32-bit and 64-bit)
  - Linux (x86, ARM, MIPS architectures)
  - macOS (basic support)
- **Dependencies**: All libraries automatically included - no manual installation
- **Permissions**: USB device access required

## Notes for P2 Series Cameras

- Default resolution: 256×192 pixels
- Temperature data requires `y16_preview_start` command (handled automatically)
- 5-second stabilization wait recommended after starting stream
- Temperature mode is enabled automatically when using `start_stream()`
- All thermal camera libraries are automatically managed - no runtime dependency issues

## Package Information

- **Package Name**: `tiny-thermal-camera`
- **Module Name**: `tiny_thermal_camera`
- **Version**: 1.0.0
- **Build System**: Cross-platform setuptools with pybind11
- **Context Manager**: Built-in (no separate wrapper needed)
- **Library Management**: Automatic DLL/library loading for all platforms
- **Architectures Supported**:
  - Windows: x86, x64
  - Linux: x86, ARM (multiple variants), MIPS
  - Cross-compilation: Full toolchain support

## Supported Linux Architectures

- **x86**: Standard Intel/AMD processors
- **ARM 64-bit**: aarch64-linux-gnu, aarch64-none-linux-gnu
- **ARM 32-bit**: arm-linux-gnueabi, arm-linux-gnueabihf
- **Embedded ARM**: arm-himix100-linux, arm-himix200-linux, arm-hisiv300/500-linux
- **MIPS**: mips-linux-gnu (limited library support)
- **Custom**: Support for buildroot and musl toolchains

## Building Wheels & Releasing

### For Maintainers

**Quick local wheel build:**
```bash
# Windows
build_wheel.bat

# Linux
./build_wheel.sh
```

**Automated release process** via GitHub Actions:
1. Update version in `pyproject.toml`
2. Create and push tag: `git tag v1.x.x && git push origin v1.x.x`
3. GitHub Actions automatically builds and publishes wheels to PyPI

See [RELEASING.md](RELEASING.md) for detailed release instructions.

### Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Tests pass (if applicable)
- Documentation is updated
- Pre-compiled wheels build successfully

## License

MIT License - This software is provided as-is for educational and development purposes.