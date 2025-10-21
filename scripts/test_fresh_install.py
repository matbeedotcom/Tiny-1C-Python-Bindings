#!/usr/bin/env python3
"""
Test the wheel as a fresh user would install it.
This creates a fresh virtual environment and tests the installation.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_command(cmd, cwd=None, capture=True):
    """Run a command and return output."""
    print(f"\n> {cmd}")
    if capture:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result
    else:
        result = subprocess.run(cmd, shell=True, cwd=cwd)
        return result

def test_fresh_install(wheel_path):
    """Test installing the wheel in a fresh virtual environment."""

    wheel_path = Path(wheel_path).absolute()
    if not wheel_path.exists():
        print(f"ERROR: Wheel not found: {wheel_path}")
        return False

    print("="*70)
    print("Testing Fresh Install")
    print("="*70)
    print(f"Wheel: {wheel_path.name}")
    print(f"Path: {wheel_path}")

    # Create temporary directory for virtual environment
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        venv_path = temp_path / "test_venv"

        print(f"\nUsing temporary directory: {temp_path}")

        # Create virtual environment
        print("\n" + "="*70)
        print("Step 1: Creating fresh virtual environment")
        print("="*70)
        result = run_command(f'python -m venv "{venv_path}"')
        if result.returncode != 0:
            print("ERROR: Failed to create virtual environment")
            return False

        # Determine venv python path
        if sys.platform == 'win32':
            venv_python = venv_path / "Scripts" / "python.exe"
            venv_pip = venv_path / "Scripts" / "pip.exe"
        else:
            venv_python = venv_path / "bin" / "python"
            venv_pip = venv_path / "bin" / "pip"

        # Upgrade pip
        print("\n" + "="*70)
        print("Step 2: Upgrading pip in virtual environment")
        print("="*70)
        result = run_command(f'"{venv_python}" -m pip install --upgrade pip')
        if result.returncode != 0:
            print("ERROR: Failed to upgrade pip")
            return False

        # Install numpy (required dependency)
        print("\n" + "="*70)
        print("Step 3: Installing numpy")
        print("="*70)
        result = run_command(f'"{venv_pip}" install numpy')
        if result.returncode != 0:
            print("ERROR: Failed to install numpy")
            return False

        # Install the wheel
        print("\n" + "="*70)
        print("Step 4: Installing the wheel")
        print("="*70)
        result = run_command(f'"{venv_pip}" install "{wheel_path}"')
        if result.returncode != 0:
            print("ERROR: Failed to install wheel")
            return False

        # Test import
        print("\n" + "="*70)
        print("Step 5: Testing module import")
        print("="*70)

        test_script = '''
import sys
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print()

# Try to import the module
try:
    import tiny_thermal_camera
    print("✓ Successfully imported tiny_thermal_camera")
    print(f"  Module location: {tiny_thermal_camera.__file__}")

    # Check if module has expected classes
    if hasattr(tiny_thermal_camera, 'ThermalCamera'):
        print("✓ ThermalCamera class found")
    else:
        print("✗ ThermalCamera class NOT found")
        sys.exit(1)

    if hasattr(tiny_thermal_camera, 'TemperatureProcessor'):
        print("✓ TemperatureProcessor class found")
    else:
        print("✗ TemperatureProcessor class NOT found")
        sys.exit(1)

    # Check for bundled DLLs (Windows)
    if sys.platform == 'win32':
        module_dir = os.path.dirname(tiny_thermal_camera.__file__)

        # Check for DLLs in package directory (old setup.py style)
        dlls_dir = os.path.join(module_dir, 'dlls')
        if os.path.exists(dlls_dir):
            dll_files = os.listdir(dlls_dir)
            print(f"\\n✓ Found dlls folder with {len(dll_files)} files:")
            for dll in dll_files:
                print(f"    - {dll}")

        # Check for delvewheel .data/platlib (new style)
        site_packages = os.path.dirname(module_dir)
        data_dirs = [d for d in os.listdir(site_packages) if d.startswith('tiny_thermal_camera') and '.data' in d]
        for data_dir in data_dirs:
            platlib = os.path.join(site_packages, data_dir, 'platlib')
            if os.path.exists(platlib):
                platlib_files = os.listdir(platlib)
                print(f"\\n✓ Found delvewheel platlib with {len(platlib_files)} files:")
                for f in platlib_files:
                    print(f"    - {f}")

        # Check specifically for msvcr100.dll
        def find_dll(dll_name):
            """Search for a DLL in the installation."""
            for root, dirs, files in os.walk(site_packages):
                for file in files:
                    if file.lower() == dll_name.lower() or dll_name.lower() in file.lower():
                        return os.path.join(root, file)
            return None

        msvcr100_path = find_dll('msvcr100')
        if msvcr100_path:
            print(f"\\n✓ msvcr100.dll IS bundled: {os.path.basename(msvcr100_path)}")
        else:
            print(f"\\n✗ msvcr100.dll NOT found - this may cause runtime errors!")

    # Try to create a ThermalCamera instance (will fail without hardware, but tests DLL loading)
    print("\\nAttempting to create ThermalCamera instance...")
    try:
        camera = tiny_thermal_camera.ThermalCamera()
        print("✗ Unexpected: Camera created without hardware!")
    except RuntimeError as e:
        # Expected error when no camera is connected
        if "Failed to open camera" in str(e) or "No camera found" in str(e):
            print(f"✓ Got expected error (no hardware): {e}")
        else:
            print(f"✗ Unexpected error: {e}")
            sys.exit(1)
    except Exception as e:
        # Check if it's a DLL loading error
        if "DLL" in str(e) or "library" in str(e).lower():
            print(f"✗ DLL LOADING ERROR: {e}")
            sys.exit(1)
        else:
            print(f"? Unexpected exception type: {type(e).__name__}: {e}")
            sys.exit(1)

    print("\\n" + "="*70)
    print("✅ All tests passed!")
    print("="*70)
    sys.exit(0)

except ImportError as e:
    print(f"✗ Failed to import tiny_thermal_camera: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

        result = run_command(f'"{venv_python}" -c "{test_script}"')
        if result.returncode != 0:
            print("\n" + "="*70)
            print("❌ Test FAILED")
            print("="*70)
            return False

        print("\n" + "="*70)
        print("✅ Fresh install test PASSED!")
        print("="*70)
        print("\nThe wheel can be safely distributed to users.")
        return True

def main():
    """Main function."""
    if len(sys.argv) > 1:
        wheel_path = sys.argv[1]
    else:
        # Look for wheel in wheelhouse directory
        wheelhouse = Path("wheelhouse")
        if wheelhouse.exists():
            wheels = list(wheelhouse.glob("*.whl"))
            if wheels:
                wheel_path = wheels[0]
                print(f"Using wheel: {wheel_path}")
            else:
                print("ERROR: No wheels found in wheelhouse/")
                print("\nUsage: python test_fresh_install.py [wheel_path]")
                sys.exit(1)
        else:
            print("ERROR: No wheel specified and wheelhouse/ not found")
            print("\nUsage: python test_fresh_install.py [wheel_path]")
            sys.exit(1)

    success = test_fresh_install(wheel_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
