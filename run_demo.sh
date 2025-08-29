#!/bin/bash
# Run demo script for thermal camera

set -e

echo "========================================="
echo "Thermal Camera Demo Runner"
echo "========================================="

# Check if Python module is built
if ! ls tiny_thermal_camera*.so 1> /dev/null 2>&1; then
    echo "Python module not found. Building..."
    ./build.sh
fi

# Check camera connection
echo ""
echo "Checking for thermal camera..."
if lsusb | grep -q "0bda:5840"; then
    echo "✓ Thermal camera detected (USB)"
else
    echo "✗ Thermal camera not detected"
    echo "Please connect the P2/Tiny1C thermal camera and try again."
    exit 1
fi

# Check permissions
echo ""
echo "Checking USB permissions..."
DEVICE=$(lsusb | grep "0bda:5840" | awk '{print "/dev/bus/usb/" $2 "/" substr($4,1,3)}')
if [ -w "$DEVICE" ]; then
    echo "✓ USB device is writable"
else
    echo "✗ USB device is not writable"
    echo "Fixing permissions..."
    sudo chmod 666 $DEVICE
    echo "✓ Permissions fixed"
fi

# Run the demo
echo ""
echo "Starting thermal camera demo..."
echo "========================================="
python3 thermal_camera_demo.py

echo ""
echo "Demo completed!"