# Thermal Camera Python Bindings

Python bindings for the AC010_256 thermal camera SDK, supporting P2/Tiny1C thermal cameras.

## Features

- **Camera Control**: Open/close camera, start/stop streaming
- **Temperature Measurement**: Point, line, and area temperature analysis  
- **Real-time Data**: Get temperature and image frames as NumPy arrays
- **Easy Integration**: Simple Python API with context manager support
- **Comprehensive Examples**: Demo scripts and utilities included

## Installation

### Prerequisites

```bash
# Install system dependencies
sudo apt update
sudo apt install libopencv-dev pkg-config build-essential

# Install Python dependencies
pip install -r requirements.txt
```

### Build the Extension

```bash
# Build the Python extension in-place
python3 setup.py build_ext --inplace

# Or install it system-wide
pip install .
```

## Usage

### Quick Start

```python
from tiny_thermal_camera import TinyThermalCamera

# Context manager automatically handles open/close
with TinyThermalCamera() as camera:
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

### Advanced Usage

```python
import thermal_camera
import numpy as np

# Direct API access
camera = thermal_camera.ThermalCamera()
temp_processor = thermal_camera.TemperatureProcessor()

if camera.open():
    camera.start_stream()
    
    # Get camera info
    width, height, fps = camera.get_camera_info()
    
    # Get raw temperature frame
    temp_frame = camera.get_temperature_frame()
    
    # Point temperature
    success, temp = temp_processor.get_point_temp(temp_frame, 128, 96)
    if success:
        print(f"Temperature at center: {temp:.1f}°C")
    
    # Area temperature
    success, max_t, min_t, avg_t = temp_processor.get_rect_temp(
        temp_frame, 100, 80, 50, 50)
    if success:
        print(f"Area stats - Max: {max_t:.1f}°C, Min: {min_t:.1f}°C, Avg: {avg_t:.1f}°C")
    
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

### Simple Test

```bash
python3 tiny_thermal_camera.py
```

Basic functionality test with temperature statistics.

## API Reference

### ThermalCamera Class

#### Methods
- `open()` - Open the thermal camera
- `close()` - Close the camera
- `start_stream()` - Start video streaming
- `stop_stream()` - Stop streaming
- `get_camera_info()` - Get (width, height, fps)
- `get_temperature_frame()` - Get temperature data as uint16 numpy array
- `get_image_frame()` - Get visual image as uint8 numpy array
- `is_open()` - Check if camera is open
- `is_streaming()` - Check if streaming

### TemperatureProcessor Class

#### Static Methods
- `temp_to_celsius(raw_value)` - Convert raw temperature to Celsius
- `get_point_temp(frame, x, y)` - Get temperature at point
- `get_rect_temp(frame, x, y, w, h)` - Get area temperature stats
- `get_line_temp(frame, x1, y1, x2, y2)` - Get line temperature stats

### TinyThermalCamera Class

#### Context Manager Support
```python
with TinyThermalCamera() as camera:
    # Automatic open/close
    pass
```

#### Methods
- `capture_frame()` - Get (temp_frame, image_frame)
- `get_temperature_celsius(temp_frame)` - Convert frame to Celsius
- `get_temperature_stats(temp_frame)` - Get comprehensive statistics
- `find_hotspot(temp_frame)` - Find hottest point
- `find_coldspot(temp_frame)` - Find coldest point

## Troubleshooting

### Camera Not Found
```bash
# Check USB connection
lsusb | grep 0bda:5840

# Fix permissions
sudo chmod 666 /dev/bus/usb/*/007
```

### Build Errors
```bash
# Install missing dependencies
sudo apt install libopencv-dev pkg-config

# Check OpenCV
pkg-config opencv4 --cflags --libs

# Clean and rebuild
python3 setup.py clean --all
python3 setup.py build_ext --inplace
```

### Import Errors
```bash
# Make sure extension is built
ls -la thermal_camera*.so

# Check Python path
python3 -c "import sys; print(sys.path)"
```

## Hardware Requirements

- **Compatible Cameras**: P2 series, Tiny1C, AC010_256
- **Connection**: USB interface
- **OS**: Linux (tested on Ubuntu 20.04+)
- **Permissions**: USB device access required

## Notes for P2 Series Cameras

- Default resolution: 256×384 pixels
- Temperature data requires `y16_preview_start` command
- 5-second stabilization wait recommended after starting stream
- Resolution switching requires specific sequence (handled automatically)

## License

This software is provided as-is for educational and development purposes.