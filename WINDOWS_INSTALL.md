# Windows Installation Guide

This guide provides step-by-step instructions for installing the `tiny-thermal-camera` package on Windows.

## Prerequisites

### 1. Microsoft Visual C++ Build Tools (Required)

The package requires C++ compilation tools to build the native extension module.

**Installation Options:**

#### Option A: Visual Studio Build Tools (Recommended - ~7GB)
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer
3. Select "Desktop development with C++"
4. Install (this will take some time)

#### Option B: Visual Studio Community Edition (Full IDE - ~10GB)
1. Download from: https://visualstudio.microsoft.com/downloads/
2. Run the installer
3. Select "Desktop development with C++" workload
4. Install

**Verification:**
```bash
# After installation, verify the compiler is available:
where cl
# Should show path to cl.exe
```

### 2. Python Requirements
- Python 3.6 or higher
- pip (usually comes with Python)

## Installation Methods

### Method 1: Install from PyPI (When Available)

```bash
pip install tiny-thermal-camera
```

### Method 2: Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/matbeedotcom/Tiny-1C-Python-Bindings.git
cd Tiny-1C-Python-Bindings

# Install in development mode
pip install -e .

# Or build and install
pip install .
```

### Method 3: Build Extension Only

```bash
# Build the extension module in-place
python setup_crossplatform.py build_ext --inplace

# Or use the build script
build_windows.bat
```

## Troubleshooting

### Error: "Microsoft Visual C++ 14.0 or greater is required"

**Solution:** Install Microsoft Visual C++ Build Tools (see Prerequisites above)

### Error: "x64 DLLs not found, build may fail"

This is usually just a warning. The build system will use the correct libraries automatically.

If the build actually fails:
1. Verify the `libs/win/x64/dll/` directory contains:
   - libiruvc.dll and libiruvc.lib
   - libirtemp.dll and libirtemp.lib
   - libirprocess.dll and libirprocess.lib
   - libirparse.dll and libirparse.lib

2. Check your Python architecture:
   ```bash
   python -c "import platform; print(platform.architecture())"
   ```
   - For 64-bit Python: Should use x64 libraries
   - For 32-bit Python: Should use Win32 libraries

### Error: "DLL package not found"

This is a warning during package preparation. The extension will still build correctly.

### OpenCV Headers Warning

The package includes local OpenCV headers for basic functionality. You don't need to install OpenCV separately unless you're using the visualization examples.

## Verifying Installation

After installation, verify the package works:

```python
import tiny_thermal_camera
print("Package imported successfully!")

# Check version
print(dir(tiny_thermal_camera))
```

## Runtime Requirements

The built package requires these DLLs at runtime (automatically included):
- libiruvc.dll
- libirtemp.dll
- libirprocess.dll
- libirparse.dll
- pthreadVC2.dll
- Microsoft Visual C++ Runtime (msvcp140.dll, vcruntime140.dll)

These are bundled with the package and should work automatically.

## USB Permissions (Camera Access)

When using the thermal camera:
1. Connect the camera via USB
2. Windows should automatically load the WinUSB driver
3. If the camera is not detected, you may need to install WinUSB driver manually using Zadig:
   - Download Zadig: https://zadig.akeo.ie/
   - Run Zadig
   - Select your camera device (VID: 0x0BDA, PID: 0x5840)
   - Select WinUSB driver
   - Install

## Common Issues

### ImportError when importing the module

**Symptom:**
```
ImportError: DLL load failed while importing tiny_thermal_camera
```

**Solution:**
1. Ensure Microsoft Visual C++ Redistributable is installed
2. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe (for 64-bit Python)
3. Install the redistributable

### Package builds but fails at runtime

Make sure all required DLLs are in the same directory as the `.pyd` file, or in your system PATH.

## Support

For issues or questions:
- GitHub Issues: https://github.com/matbeedotcom/Tiny-1C-Python-Bindings/issues
- Check existing examples: `test_simple.py`, `test_continuous.py`

## Next Steps

After successful installation:
1. See [README.md](README.md) for usage examples
2. Run `python test_simple.py` to test basic functionality
3. Run `python thermal_camera_demo.py` for interactive demo
