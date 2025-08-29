#!/bin/bash
# Build script for thermal camera Python bindings

set -e  # Exit on error

echo "========================================="
echo "Thermal Camera Python Bindings Build"
echo "========================================="

# Check for required dependencies
echo "Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed"
    exit 1
fi
echo "✓ pip found"

# Check g++
if ! command -v g++ &> /dev/null; then
    echo "Error: g++ compiler is not installed"
    echo "Install with: sudo apt install build-essential"
    exit 1
fi
echo "✓ g++ found: $(g++ --version | head -n1)"

# Check pkg-config
if ! command -v pkg-config &> /dev/null; then
    echo "Error: pkg-config is not installed"
    echo "Install with: sudo apt install pkg-config"
    exit 1
fi
echo "✓ pkg-config found"

# Check OpenCV
if ! pkg-config --exists opencv4 2>/dev/null; then
    echo "Warning: OpenCV 4 not found via pkg-config"
    echo "Install with: sudo apt install libopencv-dev"
    echo "Continuing anyway..."
fi

echo ""
echo "Installing Python dependencies..."
pip3 install --user pybind11 numpy

echo ""
echo "Cleaning previous builds..."
rm -rf build/
rm -f *.so
rm -f tiny_thermal_camera*.so

echo ""
echo "Building C++ sample application..."
make clean
make

echo ""
echo "Building Python bindings..."
python3 setup_simple.py build_ext --inplace

echo ""
echo "Verifying build..."
if [ -f tiny_thermal_camera*.so ]; then
    echo "✓ Python module built successfully: $(ls tiny_thermal_camera*.so)"
else
    echo "✗ Python module build failed"
    exit 1
fi

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "========================================="
echo ""
echo "To test the Python bindings, run:"
echo "  python3 test_simple.py"
echo ""
echo "To use in your own Python scripts:"
echo "  import tiny_thermal_camera"
echo ""