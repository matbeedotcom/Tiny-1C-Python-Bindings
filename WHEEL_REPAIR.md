# Wheel Repair Documentation

This document explains how platform-specific wheel repairs work for bundling DLLs (Windows) and shared libraries (Linux) into Python wheels.

## Overview

The `tiny-thermal-camera` package requires platform-specific binary libraries to function:
- **Windows**: 4 DLLs (libiruvc.dll, libirtemp.dll, libirprocess.dll, libirparse.dll) + MSVC runtime DLLs
- **Linux**: 4 shared libraries (.so files) + libusb-1.0

These libraries must be bundled into the wheel so users don't need to manually install them.

## How It Works

### Windows - delvewheel

**Tool**: [delvewheel](https://github.com/adang1345/delvewheel)

**What it does**:
1. Analyzes the Python extension module (.pyd file) to find DLL dependencies
2. Copies required DLLs into a `.libs` folder inside the wheel
3. Patches the extension module to load DLLs from the `.libs` folder
4. Includes MSVC runtime DLLs (vcruntime140.dll, msvcp140.dll, etc.)

**Configuration** (pyproject.toml:106):
```toml
repair-wheel-command = "delvewheel repair --add-path libs/win/x64/dll -w {dest_dir} {wheel}"
```

**Workflow** (build-wheels.yml:67):
```yaml
CIBW_REPAIR_WHEEL_COMMAND_WINDOWS: delvewheel repair --add-path libs/win/x64/dll --no-dll msvcr100.dll -w {dest_dir} {wheel}
```

**Key points**:
- `--add-path libs/win/x64/dll` tells delvewheel where to find our DLLs
- `--no-dll msvcr100.dll` prevents bundling old MSVC runtime (if present)
- DLLs are automatically discovered by analyzing the .pyd import table

### Linux - auditwheel

**Tool**: [auditwheel](https://github.com/pypa/auditwheel)

**What it does**:
1. Analyzes the Python extension module (.so file) to find shared library dependencies
2. Checks if dependencies are part of the manylinux standard
3. Copies non-standard libraries into a `.libs` folder with mangled names
4. Patches the extension module's RPATH to load from `.libs` folder
5. Tags the wheel with appropriate manylinux version

**Configuration** (pyproject.toml:88):
```toml
repair-wheel-command = "auditwheel repair -w {dest_dir} {wheel}"
```

**Workflow** (build-wheels.yml:66):
```yaml
CIBW_REPAIR_WHEEL_COMMAND_LINUX: auditwheel repair -w {dest_dir} {wheel}
```

**Key points**:
- Automatically bundles our custom libraries (libiruvc.so, etc.)
- Bundles libusb-1.0 since it's not in manylinux standard
- Uses static libraries (.a files) during build, but system libusb at runtime (which auditwheel bundles)
- Ensures wheel is portable across Linux distributions

## Build Process

### CI/CD (GitHub Actions)

The `.github/workflows/build-wheels.yml` workflow:

1. **Sets up environment** (lines 24-35):
   - Checks out code
   - Installs Python 3.11
   - Installs cibuildwheel

2. **Builds wheels** (lines 37-67):
   - Uses cibuildwheel to build for multiple Python versions (3.8-3.12)
   - Installs build dependencies (pybind11, numpy, delvewheel on Windows)
   - Builds extension module
   - **Repairs wheel with platform-specific tool**

3. **Linux-specific** (lines 56, 66):
   - Installs libusb-devel before building
   - Uses auditwheel to repair

4. **Windows-specific** (lines 57, 67):
   - Installs delvewheel before building
   - Uses delvewheel with `--add-path libs/win/x64/dll`

5. **Uploads artifacts** (lines 75-78):
   - Stores wheels for later download/publishing

### Local Testing

#### Windows
```bash
# Run the automated test script
scripts\build_and_test_wheel.bat

# Or manually:
python -m build --wheel
python -m pip install delvewheel
delvewheel repair --add-path libs/win/x64/dll -w wheelhouse dist/*.whl
python scripts/test_wheel_repair.py
```

#### Linux
```bash
# Run the automated test script
./scripts/build_and_test_wheel.sh

# Or manually:
python3 -m build --wheel
python3 -m pip install auditwheel
auditwheel repair -w wheelhouse dist/*.whl
python3 scripts/test_wheel_repair.py
```

## Verification

The `scripts/test_wheel_repair.py` script verifies:

1. **Opens the wheel file** (it's just a ZIP archive)
2. **Lists all files** to see what's included
3. **Checks for required libraries**:
   - Windows: libiruvc.dll, libirtemp.dll, libirprocess.dll, libirparse.dll
   - Linux: libiruvc.so, libirtemp.so, libirprocess.so, libirparse.so
4. **Checks for .libs folder** (indicates successful repair)
5. **Checks for extension module** (.pyd on Windows, .so on Linux)

Example output:
```
======================================================================
Analyzing wheel: tiny_thermal_camera-1.0.0-cp311-cp311-win_amd64.whl
======================================================================

All files in wheel:
  tiny_thermal_camera-1.0.0.dist-info/...
  tiny_thermal_camera.cp311-win_amd64.pyd
  tiny_thermal_camera.libs/libiruvc.dll
  tiny_thermal_camera.libs/libirtemp.dll
  tiny_thermal_camera.libs/libirprocess.dll
  tiny_thermal_camera.libs/libirparse.dll
  tiny_thermal_camera.libs/msvcp140.dll
  tiny_thermal_camera.libs/vcruntime140.dll
  ...

Checking Windows DLLs...
Found 10 DLL files:
  ✓ tiny_thermal_camera.libs/libiruvc.dll
  ✓ tiny_thermal_camera.libs/libirtemp.dll
  ...

✅ All required Windows DLLs are bundled!
```

## Common Issues

### Windows

**Issue**: DLLs not found during repair
```
Error: DLL not found: libiruvc.dll
```
**Solution**: Ensure `libs/win/x64/dll` contains all required DLLs and import libraries (.lib files)

**Issue**: MSVC runtime conflicts
```
Error: multiple versions of MSVC runtime
```
**Solution**: Use `--no-dll msvcr100.dll` to exclude old runtime versions

### Linux

**Issue**: Wheel is not manylinux compliant
```
Error: wheel is not manylinux compatible
```
**Solution**:
- Ensure all libraries are compiled with `-fPIC`
- Use static libraries during build (USE_SHARED=0)
- Let auditwheel bundle dynamic dependencies

**Issue**: Library not found during runtime
```
ImportError: libusb-1.0.so.0: cannot open shared object file
```
**Solution**: This means auditwheel didn't bundle libusb. Check:
- Is libusb-devel installed during build?
- Is the library linked dynamically (not statically)?
- Run `ldd` on the .so file to see dependencies

**Issue**: Cannot repair wheel (not on manylinux)
```
Error: cannot repair wheel on this platform
```
**Solution**: auditwheel requires a manylinux Docker container. Use cibuildwheel or build in Docker:
```bash
docker run -v $(pwd):/io quay.io/pypa/manylinux_2_28_x86_64 /bin/bash -c "
  cd /io &&
  python3 -m pip install build auditwheel pybind11 numpy &&
  python3 -m build --wheel &&
  auditwheel repair -w wheelhouse dist/*.whl
"
```

## Architecture-Specific Notes

### Windows x64 vs Win32

- **x64 build** (setup_new.py:147-163): Uses `libs/win/x64/dll/`
- **Win32 build** (setup_new.py:164-184): Uses `libs/win/Win32/dll/` or `/lib`
- Automatically detected based on Python architecture

### Linux Architectures

Current CI builds only x86_64. ARM/MIPS require cross-compilation:

**For ARM64** (aarch64):
```bash
# Would need cross-compilation toolchain
CROSS_COMPILE=aarch64-linux-gnu python3 -m build --wheel
```

**Note**: Cross-compiled wheels can't use auditwheel on x86_64 host. Need native ARM builder or QEMU.

## Testing Installed Wheels

After installing a wheel, verify libraries are bundled:

### Windows
```python
import tiny_thermal_camera
import os
import sys

# Check where module is installed
print(f"Module location: {tiny_thermal_camera.__file__}")

# Check if .libs folder exists
module_dir = os.path.dirname(tiny_thermal_camera.__file__)
libs_dir = os.path.join(module_dir, '.libs')
if os.path.exists(libs_dir):
    print(f"✓ .libs folder exists: {libs_dir}")
    print(f"  DLLs: {os.listdir(libs_dir)}")
else:
    print("✗ .libs folder NOT found - DLLs may not be bundled!")
```

### Linux
```bash
# Check RPATH and dependencies
python3 -c "import tiny_thermal_camera; print(tiny_thermal_camera.__file__)"
ldd /path/to/tiny_thermal_camera.cpython-311-x86_64-linux-gnu.so

# Should show libraries loaded from .libs folder, not system paths
```

## References

- [PEP 513 - manylinux](https://www.python.org/dev/peps/pep-0513/)
- [delvewheel documentation](https://github.com/adang1345/delvewheel)
- [auditwheel documentation](https://github.com/pypa/auditwheel)
- [cibuildwheel documentation](https://cibuildwheel.readthedocs.io/)
