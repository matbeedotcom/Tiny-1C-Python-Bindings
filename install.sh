#!/bin/bash
# Installation script for thermal camera Python bindings

set -e  # Exit on error

echo "========================================="
echo "Thermal Camera Python Bindings Installer"
echo "========================================="

# Check if running as root (not recommended for pip install)
if [ "$EUID" -eq 0 ]; then 
   echo "Warning: Running as root. Consider running as regular user."
   echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
   sleep 5
fi

# Install system dependencies
echo ""
echo "Installing system dependencies..."
echo "This may require sudo password."

# Update package list
sudo apt update

# Install build essentials
echo "Installing build tools..."
sudo apt install -y build-essential pkg-config cmake

# Install OpenCV
echo "Installing OpenCV..."
sudo apt install -y libopencv-dev

# Install Python development headers
echo "Installing Python development headers..."
sudo apt install -y python3-dev python3-pip

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install --user --upgrade pip
pip3 install --user pybind11 numpy opencv-python matplotlib

# Create udev rule for USB permissions
echo ""
echo "Setting up USB permissions..."
UDEV_RULE="/etc/udev/rules.d/99-thermal-camera.rules"
echo "Creating udev rule: $UDEV_RULE"

sudo tee $UDEV_RULE > /dev/null <<EOF
# Thermal Camera USB permissions
# P2/Tiny1C thermal camera (Realtek)
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="5840", MODE="0666", GROUP="video"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to video group
echo ""
echo "Adding user to video group..."
sudo usermod -a -G video $USER

echo ""
echo "========================================="
echo "Installation completed!"
echo "========================================="
echo ""
echo "IMPORTANT:"
echo "1. Log out and log back in for group changes to take effect"
echo "   Or run: newgrp video"
echo ""
echo "2. Build the Python bindings:"
echo "   ./build.sh"
echo ""
echo "3. Test the installation:"
echo "   python3 test_simple.py"
echo ""
echo "If you still get permission errors, you may need to:"
echo "  sudo chmod 666 /dev/bus/usb/*/[device]"
echo "Or unplug and replug the camera after logging back in."
echo ""