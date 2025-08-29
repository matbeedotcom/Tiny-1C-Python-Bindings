# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python bindings library for P2/Tiny1C thermal cameras (AC010_256 series). It provides a simplified Python API for controlling thermal cameras and processing temperature data through pybind11 C++ bindings.

## Build Commands

### Cross-Platform Build (NEW - Recommended)

#### Windows Build
```batch
# Build with DLL libraries (default)
build_windows.bat

# Build with static libraries
build_windows.bat static

# Manual build
set OPENCV_INCLUDE=C:\opencv\include
set OPENCV_LIB=C:\opencv\x64\vc15\lib
python setup_crossplatform.py build_ext --inplace
```

#### Linux Native Build
```bash
# Native build (auto-detects architecture)
python3 setup_crossplatform.py build_ext --inplace

# Development install
pip install -e .
```

#### Linux Cross-Compilation
```bash
# ARM 64-bit targets
./cross_compile.sh aarch64        # Generic ARM64
./cross_compile.sh aarch64-gnu    # ARM64 with GNU libc
./cross_compile.sh aarch64-musl   # ARM64 with musl libc

# ARM 32-bit targets  
./cross_compile.sh arm-gnueabi    # ARM soft-float
./cross_compile.sh arm-gnueabihf  # ARM hard-float
./cross_compile.sh arm-buildroot  # Buildroot ARM

# HiSilicon platforms
./cross_compile.sh arm-himix100   # HiMX100
./cross_compile.sh arm-himix200   # HiMX200
./cross_compile.sh arm-hisiv300   # V300
./cross_compile.sh arm-hisiv500   # V500

# MIPS targets
./cross_compile.sh mips           # MIPS architecture

# Manual cross-compilation
export CROSS_COMPILE=arm-linux-gnueabihf
export TARGET_ARCH=armv7l
python3 setup_crossplatform.py build_ext --inplace
```

### Legacy Build (Original setup.py)
```bash
# Original Linux x86 build
python3 setup.py build_ext --inplace

# Clean and rebuild
python3 setup.py clean --all
pip install -e . --force-reinstall
```

### C++ Sample Build (optional)
```bash
# Build C++ sample application
make sample

# Clean C++ build
make clean
```

## Testing Commands

```bash
# Basic functionality test
python3 test_simple.py

# Continuous monitoring test
python3 test_continuous.py

# Interactive demo with visualization
python3 thermal_camera_demo.py
```

## Architecture

### Core Components

1. **Python Extension Module** (`tiny_thermal_camera`)
   - `python_bindings_tiny.cpp` - Main pybind11 bindings implementation
   - Links to platform-specific thermal camera libraries
   - Provides `ThermalCamera` class with context manager support
   - Provides `TemperatureProcessor` static class for temperature calculations

2. **Cross-Platform Library Structure**
   ```
   libs/
   ├── include/           # Common header files
   ├── linux/            # Linux libraries for various architectures
   │   ├── x86-linux_libs/           # x86/x64 Linux
   │   ├── aarch64-linux-gnu_libs/   # ARM 64-bit
   │   ├── arm-linux-gnueabi_libs/   # ARM 32-bit soft-float
   │   ├── arm-linux-gnueabihf_libs/ # ARM 32-bit hard-float
   │   ├── arm-himix*_libs/          # HiSilicon platforms
   │   ├── arm-hisiv*_libs/          # HiSilicon Vision platforms
   │   └── mips-linux-gnu_libs/      # MIPS architecture
   └── win/              # Windows libraries
       └── Win32/
           ├── dll/      # Dynamic libraries
           └── lib/      # Static libraries
   ```

3. **Platform-Specific Libraries**
   - **Core libraries** (all platforms):
     - `libiruvc` - USB video class interface
     - `libirtemp` - Temperature processing
     - `libirprocess` - Image processing
     - `libirparse` - Data parsing
   - **System dependencies**:
     - Linux: libusb-1.0, OpenCV4, pthread
     - Windows: winusb, setupapi, OpenCV

4. **Key Classes**
   - `TinyThermalCamera` (C++) - Low-level camera interface
   - `ThermalCamera` (Python) - High-level Python API with context manager
   - `TemperatureProcessor` (Python) - Static methods for temperature analysis

### Build System

- Uses setuptools with pybind11 for Python extension building
- Static linking of thermal camera libraries (no runtime library path issues)
- Dynamic linking for system libraries (OpenCV, libusb)
- Platform: Linux x86_64 (primary), with cross-compilation support for ARM

### Camera Communication

- USB interface (VID: 0x0BDA, PID: 0x5840)
- Resolution: 256×192 pixels
- Requires `y16_preview_start` command for temperature mode (handled automatically)
- 5-second stabilization period after stream start for P2 series

## Important Implementation Details

1. **Temperature Mode**: Always enable with `start_stream(enable_temperature_mode=True)`
2. **Context Manager**: Handles initialization/cleanup but keeps stream active after exit for continuous monitoring
3. **Frame Data**: Raw frames are uint16 numpy arrays, use `temp_to_celsius()` for conversion
4. **USB Permissions**: May require `sudo chmod 666 /dev/bus/usb/*/XXX` for device access
5. **Static Linking**: All thermal camera libraries are statically linked - simplifies deployment

## Common Development Tasks

When modifying the Python bindings:
1. Edit `python_bindings_tiny.cpp` for C++ implementation changes
2. Rebuild with `python3 setup.py build_ext --inplace`
3. Test with `python3 test_simple.py`

When adding new functionality:
1. Add C++ implementation in `python_bindings_tiny.cpp`
2. Update pybind11 module definition at the bottom of the file
3. Add Python convenience methods if needed
4. Update test files to verify functionality