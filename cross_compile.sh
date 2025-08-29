#!/bin/bash

# Cross-compilation script for Tiny Thermal Camera Python Bindings
# Supports various ARM, MIPS, and x86 targets

set -e

echo "============================================"
echo "Cross-Compilation Build Script"
echo "Tiny Thermal Camera Python Bindings"
echo "============================================"

# Function to display usage
usage() {
    echo "Usage: $0 [TARGET]"
    echo ""
    echo "Supported targets:"
    echo "  x86              - x86 Linux (32/64-bit)"
    echo "  aarch64          - ARM 64-bit (generic)"
    echo "  aarch64-gnu      - ARM 64-bit with GNU libc"
    echo "  aarch64-musl     - ARM 64-bit with musl libc"
    echo "  arm-gnueabi      - ARM 32-bit soft-float"
    echo "  arm-gnueabihf    - ARM 32-bit hard-float"
    echo "  arm-himix100     - HiSilicon HiMX100"
    echo "  arm-himix200     - HiSilicon HiMX200"
    echo "  arm-hisiv300     - HiSilicon V300"
    echo "  arm-hisiv500     - HiSilicon V500"
    echo "  arm-buildroot    - Buildroot ARM"
    echo "  mips             - MIPS architecture"
    echo ""
    echo "Environment variables:"
    echo "  CROSS_COMPILE    - Cross-compiler prefix"
    echo "  TARGET_ARCH      - Target architecture"
    echo "  USE_SHARED       - Use shared libraries (0/1, default: 0)"
    echo "  SYSROOT          - Target system root"
    echo ""
    exit 1
}

# Parse arguments
TARGET=${1:-native}

# Set cross-compilation variables based on target
case "$TARGET" in
    x86|native)
        echo "Building for native x86 Linux..."
        unset CROSS_COMPILE
        unset TARGET_ARCH
        ;;
    
    aarch64|aarch64-gnu)
        echo "Building for aarch64-linux-gnu..."
        export CROSS_COMPILE=aarch64-linux-gnu
        export TARGET_ARCH=aarch64
        export CC=aarch64-linux-gnu-gcc
        export CXX=aarch64-linux-gnu-g++
        export AR=aarch64-linux-gnu-ar
        ;;
    
    aarch64-none)
        echo "Building for aarch64-none-linux-gnu..."
        export CROSS_COMPILE=aarch64-none-linux-gnu
        export TARGET_ARCH=aarch64
        export CC=aarch64-none-linux-gnu-gcc
        export CXX=aarch64-none-linux-gnu-g++
        export AR=aarch64-none-linux-gnu-ar
        ;;
    
    aarch64-musl)
        echo "Building for aarch64-v01c01-linux-musl..."
        export CROSS_COMPILE=aarch64-v01c01-linux-musl
        export TARGET_ARCH=aarch64
        export CC=aarch64-v01c01-linux-musl-gcc
        export CXX=aarch64-v01c01-linux-musl-g++
        export AR=aarch64-v01c01-linux-musl-ar
        ;;
    
    arm-gnueabi)
        echo "Building for arm-linux-gnueabi..."
        export CROSS_COMPILE=arm-linux-gnueabi
        export TARGET_ARCH=arm
        export CC=arm-linux-gnueabi-gcc
        export CXX=arm-linux-gnueabi-g++
        export AR=arm-linux-gnueabi-ar
        ;;
    
    arm-gnueabihf)
        echo "Building for arm-linux-gnueabihf..."
        export CROSS_COMPILE=arm-linux-gnueabihf
        export TARGET_ARCH=armv7l
        export CC=arm-linux-gnueabihf-gcc
        export CXX=arm-linux-gnueabihf-g++
        export AR=arm-linux-gnueabihf-ar
        ;;
    
    arm-buildroot)
        echo "Building for arm-buildroot-linux-uclibcgnueabihf..."
        export CROSS_COMPILE=arm-buildroot-linux-uclibcgnueabihf
        export TARGET_ARCH=arm
        export CC=arm-buildroot-linux-uclibcgnueabihf-gcc
        export CXX=arm-buildroot-linux-uclibcgnueabihf-g++
        export AR=arm-buildroot-linux-uclibcgnueabihf-ar
        ;;
    
    arm-himix100)
        echo "Building for arm-himix100-linux..."
        export CROSS_COMPILE=arm-himix100-linux
        export TARGET_ARCH=arm
        export CC=arm-himix100-linux-gcc
        export CXX=arm-himix100-linux-g++
        export AR=arm-himix100-linux-ar
        ;;
    
    arm-himix200)
        echo "Building for arm-himix200-linux..."
        export CROSS_COMPILE=arm-himix200-linux
        export TARGET_ARCH=arm
        export CC=arm-himix200-linux-gcc
        export CXX=arm-himix200-linux-g++
        export AR=arm-himix200-linux-ar
        ;;
    
    arm-hisiv300)
        echo "Building for arm-hisiv300-linux-uclibcgnueabi..."
        export CROSS_COMPILE=arm-hisiv300-linux-uclibcgnueabi
        export TARGET_ARCH=arm
        export CC=arm-hisiv300-linux-uclibcgnueabi-gcc
        export CXX=arm-hisiv300-linux-uclibcgnueabi-g++
        export AR=arm-hisiv300-linux-uclibcgnueabi-ar
        ;;
    
    arm-hisiv500)
        echo "Building for arm-hisiv500-linux-uclibcgnueabi..."
        export CROSS_COMPILE=arm-hisiv500-linux-uclibcgnueabi
        export TARGET_ARCH=arm
        export CC=arm-hisiv500-linux-uclibcgnueabi-gcc
        export CXX=arm-hisiv500-linux-uclibcgnueabi-g++
        export AR=arm-hisiv500-linux-uclibcgnueabi-ar
        ;;
    
    mips)
        echo "Building for mips-linux-gnu..."
        export CROSS_COMPILE=mips-linux-gnu
        export TARGET_ARCH=mips
        export CC=mips-linux-gnu-gcc
        export CXX=mips-linux-gnu-g++
        export AR=mips-linux-gnu-ar
        ;;
    
    *)
        echo "Error: Unknown target '$TARGET'"
        usage
        ;;
esac

# Display build configuration
echo ""
echo "Build Configuration:"
echo "  TARGET: $TARGET"
echo "  CROSS_COMPILE: ${CROSS_COMPILE:-native}"
echo "  TARGET_ARCH: ${TARGET_ARCH:-native}"
echo "  USE_SHARED: ${USE_SHARED:-0}"
echo ""

# Check for cross-compiler if needed
if [ ! -z "$CROSS_COMPILE" ]; then
    if ! command -v ${CC} &> /dev/null; then
        echo "Error: Cross-compiler ${CC} not found!"
        echo "Please install the appropriate cross-compilation toolchain."
        exit 1
    fi
fi

# Install Python dependencies
echo "Installing Python build dependencies..."
pip3 install --user pybind11 numpy setuptools wheel

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.egg-info
rm -f tiny_thermal_camera*.so

# Build the extension
echo ""
echo "Building Python extension..."
python3 setup_crossplatform.py build_ext --inplace

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "Build completed successfully!"
    echo "============================================"
    echo ""
    echo "Output file: tiny_thermal_camera*.so"
    echo ""
    echo "To create a wheel package:"
    echo "  python3 setup_crossplatform.py bdist_wheel"
    echo ""
    echo "To test (if running on target platform):"
    echo "  python3 test_simple.py"
else
    echo ""
    echo "Build failed! Check the error messages above."
    exit 1
fi