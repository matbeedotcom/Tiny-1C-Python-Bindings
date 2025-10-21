#!/bin/bash
# Build and test wheel repair for Linux
# This script builds a wheel locally and verifies shared library bundling

set -e  # Exit on error

echo "========================================"
echo "Building and Testing Linux Wheel"
echo "========================================"

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist wheelhouse *.egg-info

# Install build dependencies
echo ""
echo "Installing build dependencies..."
python3 -m pip install --upgrade pip build wheel setuptools pybind11 numpy auditwheel

# Temporarily remove DLLs from src (delvewheel will bundle them on Windows)
echo ""
echo "Temporarily moving DLLs out of source tree..."
if [ -d "src/tiny_thermal_camera/dlls" ]; then
    mv src/tiny_thermal_camera/dlls src/tiny_thermal_camera/dlls_backup
fi

# Build the wheel
echo ""
echo "Building wheel..."
python3 -m build --wheel

# Restore DLLs for development
echo ""
echo "Restoring DLLs for development..."
if [ -d "src/tiny_thermal_camera/dlls_backup" ]; then
    mv src/tiny_thermal_camera/dlls_backup src/tiny_thermal_camera/dlls
fi

# Check if wheel was created
if [ ! -f dist/*.whl ]; then
    echo "ERROR: No wheel was created!"
    exit 1
fi

# Create wheelhouse directory and copy wheel
mkdir -p wheelhouse
cp dist/*.whl wheelhouse/

# Repair the wheel with auditwheel
echo ""
echo "Repairing wheel with auditwheel..."
for wheel in dist/*.whl; do
    echo "Repairing: $wheel"
    auditwheel repair -w wheelhouse "$wheel" || {
        echo "ERROR: auditwheel repair failed!"
        echo ""
        echo "This might be because:"
        echo "  1. You're not on a manylinux-compatible system"
        echo "  2. Required libraries are missing"
        echo "  3. Library dependencies are not in standard paths"
        echo ""
        echo "Checking library dependencies..."
        python3 -c "import sys; from pathlib import Path; import zipfile; z = zipfile.ZipFile('$wheel'); so_files = [f for f in z.namelist() if f.endswith('.so')]; print('Extension modules:', so_files); sys.exit(0 if so_files else 1)"
        exit 1
    }
done

# Test the repaired wheel
echo ""
echo "Testing repaired wheel..."
python3 scripts/test_wheel_repair.py

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "FAILED: Wheel repair verification failed"
    echo "========================================"
    exit 1
else
    echo ""
    echo "========================================"
    echo "SUCCESS: Wheel is properly repaired!"
    echo "========================================"
    echo ""
    echo "Repaired wheel is in: wheelhouse/"
    ls -lh wheelhouse/*.whl
fi
