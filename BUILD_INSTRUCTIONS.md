# Thermal Camera SDK Build Instructions

## Quick Start

```bash
# 1. Install dependencies (one-time setup)
./install.sh

# 2. Build everything
./build.sh

# 3. Test the Python bindings
python3 test_simple.py
```

## Build Scripts

### **install.sh** - System Setup (Run Once)
Installs all required system dependencies and configures USB permissions.
```bash
./install.sh
```
- Installs: build-essential, pkg-config, OpenCV, Python dev headers
- Sets up USB udev rules for thermal camera
- Adds user to video group

### **build.sh** - Main Build Script
Builds both C++ sample and Python bindings.
```bash
./build.sh
```
- Checks dependencies
- Builds C++ sample application
- Builds Python extension module
- Verifies build success

### **clean.sh** - Clean Build Artifacts
Removes all build artifacts and temporary files.
```bash
./clean.sh
```

### **build_cmake.sh** - Alternative CMake Build
Uses CMake instead of setuptools (optional).
```bash
./build_cmake.sh
```

## Build Methods

### Method 1: Using setuptools (Recommended)
```bash
python3 setup_simple.py build_ext --inplace
```

### Method 2: Using CMake
```bash
mkdir build && cd build
cmake -f ../CMakeLists_python.txt ..
make
```

### Method 3: Using Make (C++ only)
```bash
make clean
make
```

## Test Scripts

### **test_simple.py** - Basic Functionality Test
Tests basic camera operations and temperature reading.
```bash
python3 test_simple.py
```

### **test_continuous.py** - Continuous Monitoring
Real-time temperature monitoring with statistics.
```bash
python3 test_continuous.py
```

### **thermal_camera_demo.py** - Interactive Demo
Full-featured demo with visualization (requires matplotlib/OpenCV).
```bash
python3 thermal_camera_demo.py
```

### **run_demo.sh** - Demo Runner with Checks
Runs demo with automatic permission fixing.
```bash
./run_demo.sh
```

## Python API Usage

### Basic Example
```python
import tiny_thermal_camera
import numpy as np

# Open camera
camera = tiny_thermal_camera.ThermalCamera()
camera.initialize()
camera.open()

# Start streaming (waits 5s and enables temperature mode)
camera.start_stream(enable_temperature_mode=True, wait_seconds=5)

# Get temperature data
raw_frame = camera.get_raw_frame()
temp_celsius = np.vectorize(tiny_thermal_camera.temp_to_celsius)(raw_frame)

print(f"Temperature range: {temp_celsius.min():.1f}°C - {temp_celsius.max():.1f}°C")

# Cleanup
camera.stop_stream()
camera.close()
```

### Advanced Usage with SimpleThermalCamera wrapper
```python
from tiny_thermal_camera import SimpleThermalCamera

with SimpleThermalCamera() as camera:
    if camera.start_streaming():
        temp_frame, _ = camera.capture_frame()
        stats = camera.get_temperature_stats(temp_frame)
        print(f"Average temperature: {stats['mean']:.1f}°C")
```

## Troubleshooting

### Permission Denied
```bash
# Fix USB permissions
sudo chmod 666 /dev/bus/usb/*/007  # Replace 007 with actual device

# Or add permanent udev rule
sudo cp 99-thermal-camera.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
```

### Module Not Found
```bash
# Rebuild the module
./clean.sh
./build.sh

# Check if .so file exists
ls -la tiny_thermal_camera*.so
```

### Camera Not Detected
```bash
# Check USB connection
lsusb | grep 0bda:5840

# Check dmesg for errors
dmesg | tail -20
```

### Temperature Shows 238.9°C Constantly
The camera needs proper initialization:
- Wait 5 seconds after starting stream
- y16_preview_start command must succeed
- Check console output for "Temperature mode enabled"

## File Structure

```
.
├── Build Scripts
│   ├── build.sh              # Main build script
│   ├── clean.sh              # Clean artifacts
│   ├── install.sh            # Install dependencies
│   ├── build_cmake.sh        # CMake build
│   └── run_demo.sh           # Run demo with checks
│
├── Python Source
│   ├── python_bindings_simple.cpp   # C++ bindings
│   ├── setup_simple.py              # Python setup script
│   ├── pyproject.toml               # Modern Python packaging
│   └── requirements.txt             # Python dependencies
│
├── Test Scripts
│   ├── test_simple.py              # Basic test
│   ├── test_continuous.py          # Continuous monitoring
│   ├── thermal_camera_demo.py      # Full demo
│   └── tiny_thermal_camera.py    # Python wrapper
│
├── C++ Source
│   ├── sample.cpp                  # C++ sample
│   ├── camera.cpp/h                # Camera control
│   ├── temperature.cpp/h           # Temperature processing
│   ├── display.cpp/h               # Display functions
│   ├── data.cpp/h                  # Data structures
│   └── cmd.cpp/h                   # Command functions
│
├── Libraries
│   └── libs/linux/x86-linux_libs/  # Thermal camera libraries
│
└── Documentation
    ├── README_python.md             # Python API documentation
    └── BUILD_INSTRUCTIONS.md        # This file
```

## Requirements

- **OS**: Linux (Ubuntu 20.04+ tested)
- **Python**: 3.6+
- **Compiler**: g++ with C++11 support
- **Libraries**: OpenCV 4.x, pybind11
- **Hardware**: P2/Tiny1C thermal camera (USB)

## Support

For issues specific to:
- **Python bindings**: Check python_bindings_simple.cpp
- **Temperature data**: Check temperature mode initialization
- **USB permissions**: Run install.sh or check udev rules
- **Build errors**: Check dependencies with build.sh

## Notes

- The camera takes 5 seconds to stabilize after starting
- Temperature mode must be explicitly enabled for P2 series
- Raw values are uint16, divide by 64 and subtract 273.15 for Celsius
- Default resolution is 256×192 for P2 series cameras