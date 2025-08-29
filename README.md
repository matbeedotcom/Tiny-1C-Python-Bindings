# Tiny Thermal Camera Python Bindings

Python bindings for the AC010_256 thermal camera SDK, supporting P2/Tiny1C thermal cameras.

## Features

- **Camera Control**: Open/close camera, start/stop streaming
- **Temperature Measurement**: Point, line, and area temperature analysis  
- **Real-time Data**: Get temperature and image frames as NumPy arrays
- **Easy Integration**: Simple Python API with context manager support
- **Self-Contained**: No runtime library dependencies to manage
- **Comprehensive Examples**: Demo scripts and utilities included

## Installation

### Prerequisites

```bash
# Install system dependencies (OpenCV and libusb are required)
sudo apt update
sudo apt install libopencv-dev libusb-1.0-0-dev pkg-config build-essential python3-dev

# Python dependencies are installed automatically
```

### Build and Install

```bash
# Option 1: Development install (recommended)
pip install -e .

# Option 2: Build in-place for development
python3 setup.py build_ext --inplace

# Option 3: Regular install
pip install .
```

The module automatically handles all thermal camera library dependencies through static linking - no additional library path setup needed!

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
```

## API Reference

### tiny_thermal_camera.ThermalCamera Class

#### Context Manager Support
```python
import tiny_thermal_camera

# Automatic initialization, opening, and cleanup
with tiny_thermal_camera.ThermalCamera() as camera:
    # Camera is ready to use
    pass
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

## Troubleshooting

### Camera Not Found
```bash
# Check USB connection and device presence
lsusb | grep 0bda:5840

# Check USB permissions
ls -la /dev/bus/usb/

# Fix USB permissions (adjust bus/device numbers as needed)
sudo chmod 666 /dev/bus/usb/*/007
```

### Build Errors
```bash
# Install missing dependencies
sudo apt install libopencv-dev libusb-1.0-0-dev pkg-config build-essential python3-dev

# Check OpenCV installation
pkg-config opencv4 --cflags --libs

# Clean and rebuild
python3 setup.py clean --all
pip install -e . --force-reinstall
```

### Import Errors
```bash
# Check if module is built
ls -la tiny_thermal_camera*.so

# Test basic import
python3 -c "import tiny_thermal_camera; print('OK')"

# Check for missing system libraries
ldd tiny_thermal_camera*.so
```

### Runtime Issues
```bash
# Check device initialization
python3 -c "
import tiny_thermal_camera
camera = tiny_thermal_camera.ThermalCamera()
success, devices = camera.get_device_list()
print(f'Found {len(devices)} devices: {devices}')
"

# Test basic camera operations
python3 test_simple.py
```

## Hardware Requirements

- **Compatible Cameras**: P2 series, Tiny1C, AC010_256
- **Connection**: USB interface (VID: 0x0BDA, PID: 0x5840)
- **OS**: Linux (tested on Ubuntu 20.04+)
- **Dependencies**: OpenCV, libusb-1.0 (automatically linked)
- **Permissions**: USB device access required

## Notes for P2 Series Cameras

- Default resolution: 256×192 pixels
- Temperature data requires `y16_preview_start` command (handled automatically)
- 5-second stabilization wait recommended after starting stream
- Temperature mode is enabled automatically when using `start_stream()`
- All thermal camera libraries are statically linked - no runtime dependency issues

## Package Information

- **Package Name**: `thermal-camera-sdk`
- **Module Name**: `tiny_thermal_camera`
- **Version**: 1.0.0
- **Build System**: setuptools with pybind11
- **Context Manager**: Built-in (no separate wrapper needed)
- **Static Linking**: All thermal camera libraries embedded

## License

MIT License - This software is provided as-is for educational and development purposes.