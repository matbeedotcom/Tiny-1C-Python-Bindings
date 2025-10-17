#!/bin/bash
# Build wheel for local testing on Linux

set -e

echo "========================================"
echo "Building Wheel for Linux"
echo "========================================"
echo

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found in PATH"
    exit 1
fi

# Display Python version and architecture
echo "Python version:"
python3 --version
python3 -c "import platform; print(f'Architecture: {platform.machine()}')"
echo

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.egg-info src/*.egg-info
echo

# Install build dependencies
echo "Installing build dependencies..."
python3 -m pip install --upgrade pip setuptools wheel build cibuildwheel
echo

# Choose build method
echo "Select build method:"
echo "1. Quick build (current Python only)"
echo "2. Full build (all Python versions 3.8-3.12 using cibuildwheel)"
echo "3. Cross-compile for specific architecture"
echo
read -p "Enter choice (1, 2, or 3): " choice

case $choice in
    1)
        echo
        echo "Building wheel for current Python version..."
        python3 -m build --wheel
        echo
        echo "========================================"
        echo "Wheel built successfully!"
        echo "Location: dist/"
        ls -1 dist/*.whl
        echo "========================================"
        ;;
    2)
        echo
        echo "Building wheels for Python 3.8-3.12..."
        echo "This will take several minutes and requires Docker..."
        echo
        python3 -m cibuildwheel --platform linux --output-dir dist
        echo
        echo "========================================"
        echo "Wheels built successfully!"
        echo "Location: dist/"
        ls -1 dist/*.whl
        echo "========================================"
        ;;
    3)
        echo
        echo "Available architectures:"
        echo "  1. ARM 64-bit (aarch64)"
        echo "  2. ARM 32-bit hard-float (armv7l)"
        echo "  3. ARM HiMix100"
        echo "  4. ARM HiMix200"
        echo "  5. MIPS"
        echo
        read -p "Select architecture (1-5): " arch_choice

        case $arch_choice in
            1) ./cross_compile.sh aarch64 ;;
            2) ./cross_compile.sh arm-gnueabihf ;;
            3) ./cross_compile.sh arm-himix100 ;;
            4) ./cross_compile.sh arm-himix200 ;;
            5) ./cross_compile.sh mips ;;
            *)
                echo "Invalid architecture choice"
                exit 1
                ;;
        esac

        echo
        echo "========================================"
        echo "Cross-compiled build complete!"
        echo "Binary location: build/"
        echo "========================================"
        ;;
    *)
        echo "Invalid choice. Please run again and select 1, 2, or 3."
        exit 1
        ;;
esac

echo
echo "To install the wheel:"
echo "  pip install dist/[wheel-name].whl"
echo
echo "To test the package:"
echo "  python3 -c 'import tiny_thermal_camera; print(\"Success!\")'"
echo
