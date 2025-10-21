#!/usr/bin/env python3
"""
Quick script to verify msvcr100.dll is bundled in the installed package.
Run this AFTER installing the wheel in a fresh environment.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    import tiny_thermal_camera

    print("="*70)
    print("Checking for msvcr100.dll in installed package")
    print("="*70)

    module_file = tiny_thermal_camera.__file__
    print(f"\nModule location: {module_file}")

    module_dir = os.path.dirname(module_file)
    site_packages = os.path.dirname(module_dir)

    print(f"Site-packages: {site_packages}")

    # Search for msvcr100.dll
    found_dlls = []
    for root, dirs, files in os.walk(site_packages):
        for file in files:
            if 'msvcr100' in file.lower():
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, site_packages)
                found_dlls.append((rel_path, full_path))

    print(f"\n{'='*70}")
    if found_dlls:
        print(f"✓ Found {len(found_dlls)} msvcr100.dll file(s):")
        for rel_path, full_path in found_dlls:
            size = os.path.getsize(full_path) / 1024
            print(f"  - {rel_path}")
            print(f"    Size: {size:.1f} KB")
        print("\n✓ msvcr100.dll IS bundled - package will work on systems without VS 2010 runtime!")
    else:
        print("✗ msvcr100.dll NOT found!")
        print("\n⚠ Warning: Package may fail on systems without Visual Studio 2010 runtime")
        print("          This is required by pthreadVC2.dll")
    print("="*70)

    # Also check for other important DLLs
    print("\nChecking for other thermal camera DLLs...")
    required_dlls = ['libiruvc', 'libirtemp', 'libirprocess', 'libirparse', 'pthreadvc2']

    for dll_name in required_dlls:
        found = False
        for root, dirs, files in os.walk(site_packages):
            for file in files:
                if dll_name.lower() in file.lower() and file.endswith('.dll'):
                    found = True
                    break
            if found:
                break

        if found:
            print(f"  ✓ {dll_name}.dll found")
        else:
            print(f"  ✗ {dll_name}.dll NOT found")

    # Test DLL loading by creating camera instance
    print("\n" + "="*70)
    print("Testing DLL loading (will fail without camera hardware)...")
    print("="*70)

    try:
        camera = tiny_thermal_camera.ThermalCamera()
        print("⚠ Unexpected: Camera created (is hardware connected?)")
    except RuntimeError as e:
        if "Failed to open camera" in str(e) or "camera" in str(e).lower():
            print(f"✓ DLLs loaded successfully!")
            print(f"  (Got expected error about missing hardware: {e})")
        else:
            print(f"✗ Unexpected RuntimeError: {e}")
            sys.exit(1)
    except ImportError as e:
        print(f"✗ DLL IMPORT ERROR: {e}")
        print("  This usually means a required DLL is missing!")
        sys.exit(1)
    except Exception as e:
        if "DLL" in str(e) or "0xc000007b" in str(e).lower():
            print(f"✗ DLL LOADING ERROR: {e}")
            sys.exit(1)
        else:
            print(f"✓ DLLs loaded (got different error: {type(e).__name__})")

    print("\n" + "="*70)
    print("✅ Package verification complete!")
    print("="*70)

except ImportError as e:
    print(f"✗ Cannot import tiny_thermal_camera: {e}")
    print("\nMake sure you've installed the package first:")
    print("  pip install tiny-thermal-camera")
    sys.exit(1)
