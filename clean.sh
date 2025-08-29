#!/bin/bash
# Clean script for thermal camera project

echo "Cleaning thermal camera project..."

# Clean C++ build artifacts
echo "Cleaning C++ artifacts..."
make clean 2>/dev/null || true
rm -f sample
rm -f *.o
rm -f libs_version.txt

# Clean Python build artifacts
echo "Cleaning Python build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -f *.so
rm -f thermal_camera_simple*.so
rm -f thermal_camera*.so

# Clean Python cache
echo "Cleaning Python cache..."
rm -rf __pycache__/
rm -f *.pyc
rm -f *.pyo

# Clean temporary files
echo "Cleaning temporary files..."
rm -f *~
rm -f .*.swp
rm -f .*.swo

echo "Clean complete!"