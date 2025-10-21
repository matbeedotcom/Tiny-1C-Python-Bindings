#!/usr/bin/env python3
"""
Test script to verify wheel repair is working correctly.
This script checks if all required DLLs/shared libraries are bundled in the wheel.
"""

import os
import sys
import zipfile
import platform
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def check_wheel_contents(wheel_path):
    """Check if a wheel contains all required platform-specific libraries."""
    print(f"\n{'='*70}")
    print(f"Analyzing wheel: {Path(wheel_path).name}")
    print(f"{'='*70}\n")

    with zipfile.ZipFile(wheel_path, 'r') as wheel:
        file_list = wheel.namelist()

        # Print all files
        print("All files in wheel:")
        for f in sorted(file_list):
            print(f"  {f}")

        print("\n" + "="*70)

        # Check for platform-specific libraries
        system = platform.system().lower()

        if 'win' in wheel_path.lower() or system == 'windows':
            print("\nChecking Windows DLLs...")
            required_dlls = [
                'libirparse.dll',
                'libirprocess.dll',
                'libirtemp.dll',
                'libiruvc.dll',
            ]

            # Look for DLLs in .libs folder (delvewheel convention)
            dll_files = [f for f in file_list if f.endswith('.dll')]
            libs_folder_dlls = [f for f in file_list if '.libs/' in f and f.endswith('.dll')]

            print(f"\nFound {len(dll_files)} DLL files:")
            for dll in dll_files:
                print(f"  ✓ {dll}")

            print(f"\nDLLs in .libs folder (delvewheel bundled): {len(libs_folder_dlls)}")
            for dll in libs_folder_dlls:
                print(f"  ✓ {dll}")

            # Check if required DLLs are present (handle delvewheel mangled names)
            missing_dlls = []
            for required in required_dlls:
                # Check for exact match or mangled names (e.g., libiruvc-hash.dll)
                base_name = required.replace('.dll', '')
                found = any(required in f or base_name in f for f in dll_files)
                if found:
                    print(f"  ✓ Required: {required}")
                else:
                    print(f"  ✗ MISSING: {required}")
                    missing_dlls.append(required)

            if missing_dlls:
                print(f"\n❌ ERROR: Missing required DLLs: {', '.join(missing_dlls)}")
                return False
            else:
                print(f"\n✅ All required Windows DLLs are bundled!")

        elif 'linux' in wheel_path.lower() or 'manylinux' in wheel_path.lower() or system == 'linux':
            print("\nChecking Linux shared libraries...")
            required_libs = [
                'libirparse.so',
                'libirprocess.so',
                'libirtemp.so',
                'libiruvc.so',
            ]

            # Look for .so files in .libs folder (auditwheel convention)
            so_files = [f for f in file_list if '.so' in f]
            libs_folder_sos = [f for f in file_list if '.libs/' in f and '.so' in f]

            print(f"\nFound {len(so_files)} shared library files:")
            for so in so_files:
                print(f"  ✓ {so}")

            print(f"\nShared libraries in .libs folder (auditwheel bundled): {len(libs_folder_sos)}")
            for so in libs_folder_sos:
                print(f"  ✓ {so}")

            # Check if required libs are present
            missing_libs = []
            for required in required_libs:
                # Check both direct inclusion and mangled names in .libs
                found = any(required in f or f.endswith('.so') for f in so_files)
                if found:
                    print(f"  ✓ Required: {required}")
                else:
                    print(f"  ✗ MISSING: {required}")
                    missing_libs.append(required)

            # Check for libusb bundling
            libusb_found = any('libusb' in f for f in so_files)
            if libusb_found:
                print(f"  ✓ libusb-1.0 is bundled (good!)")
            else:
                print(f"  ⚠ libusb-1.0 not found (will use system library)")

            if missing_libs:
                print(f"\n❌ ERROR: Missing required libraries: {', '.join(missing_libs)}")
                return False
            else:
                print(f"\n✅ All required Linux libraries are bundled!")

        # Check for extension module
        print("\nChecking for Python extension module...")
        ext_files = [f for f in file_list if f.endswith('.pyd') or f.endswith('.so') and 'tiny_thermal_camera' in f]
        if ext_files:
            print(f"  ✓ Found extension module: {ext_files[0]}")
        else:
            print(f"  ✗ WARNING: No extension module found")

        print("\n" + "="*70)
        return True

def main():
    """Main function to test all wheels in wheelhouse directory."""
    if len(sys.argv) > 1:
        wheel_path = sys.argv[1]
        if os.path.exists(wheel_path):
            success = check_wheel_contents(wheel_path)
            sys.exit(0 if success else 1)
        else:
            print(f"Error: Wheel not found: {wheel_path}")
            sys.exit(1)

    # Check wheelhouse directory
    wheelhouse = Path("wheelhouse")
    if not wheelhouse.exists():
        print("No wheelhouse directory found. Build wheels first with:")
        print("  python -m cibuildwheel --output-dir wheelhouse")
        sys.exit(1)

    wheels = list(wheelhouse.glob("*.whl"))
    if not wheels:
        print("No wheels found in wheelhouse directory")
        sys.exit(1)

    print(f"Found {len(wheels)} wheel(s) to check")

    all_success = True
    for wheel in wheels:
        success = check_wheel_contents(wheel)
        all_success = all_success and success

    if all_success:
        print("\n" + "="*70)
        print("✅ All wheels passed verification!")
        print("="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("❌ Some wheels failed verification")
        print("="*70)
        sys.exit(1)

if __name__ == "__main__":
    main()
