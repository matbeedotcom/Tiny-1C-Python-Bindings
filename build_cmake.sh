#!/bin/bash
# CMake build script for thermal camera Python bindings

set -e

echo "========================================="
echo "CMake Build for Thermal Camera Python"
echo "========================================="

# Create build directory
echo "Creating build directory..."
mkdir -p build_cmake
cd build_cmake

# Configure with CMake
echo "Configuring with CMake..."
cmake -DCMAKE_BUILD_TYPE=Release \
      -DPYTHON_EXECUTABLE=$(which python3) \
      -DCMAKE_PREFIX_PATH="$(python3 -c 'import pybind11; print(pybind11.get_cmake_dir())')" \
      -DCMAKE_VERBOSE_MAKEFILE=ON \
      -DCMAKE_CXX_FLAGS="-O3 -Wall" \
      -f ../CMakeLists_python.txt \
      ..

# Build
echo "Building..."
make -j$(nproc)

# Install (copy to parent directory)
echo "Installing..."
make install

cd ..

echo ""
echo "========================================="
echo "CMake build completed successfully!"
echo "========================================="
echo ""
echo "Python module installed: thermal_camera_simple.so"
echo "C++ sample installed: sample"
echo ""
echo "To test:"
echo "  python3 test_simple.py"
echo ""