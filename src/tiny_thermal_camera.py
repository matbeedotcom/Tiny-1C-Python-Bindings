"""
Tiny Thermal Camera SDK - Python bindings for P2/Tiny1C thermal cameras

This package provides Python bindings for the AC010_256 thermal camera series.
It offers simplified API for controlling thermal cameras and processing temperature data.

Key Features:
- Cross-platform support (Windows, Linux)
- Multiple architecture support (x86, ARM, MIPS)
- Camera control (open/close, start/stop streaming)
- Raw frame acquisition and temperature processing
- NumPy array integration
- Context manager support for automatic resource management

Example Usage:
    ```python
    import tiny_thermal_camera as ttc
    
    # Basic usage with context manager
    with ttc.ThermalCamera() as camera:
        if camera.is_opened():
            camera.start_stream(enable_temperature_mode=True)
            
            # Wait for stabilization (P2 series needs ~5 seconds)
            time.sleep(5)
            
            # Capture frame
            frame = camera.get_frame()
            if frame is not None:
                # Convert raw data to temperature
                temp_celsius = ttc.TemperatureProcessor.temp_to_celsius(frame)
                print(f"Temperature range: {temp_celsius.min():.1f}°C - {temp_celsius.max():.1f}°C")
    ```

Hardware Requirements:
- P2/Tiny1C thermal camera (AC010_256 series)
- USB connection (VID: 0x0BDA, PID: 0x5840)
- Proper USB permissions on Linux systems

Note: The camera requires y16_preview_start command for temperature mode,
which is handled automatically by this library.
"""

import os
import sys
import platform
from pathlib import Path
import warnings

__version__ = "1.0.0"
__author__ = "Thermal Camera Python Bindings"

def setup_library_search_path():
    """Add library directory to search path for the current platform"""
    system = platform.system().lower()
    
    # Get the directory containing this module
    module_dir = Path(__file__).parent
    
    if system == 'windows':
        # Windows: Load DLLs
        return setup_windows_dlls(module_dir)
    elif system == 'linux':
        # Linux: Set up library paths
        return setup_linux_libraries(module_dir)
    else:
        # Other platforms (macOS, etc.) - basic setup
        return True

def setup_windows_dlls(module_dir):
    """Setup Windows DLL loading"""
    dll_dir = module_dir / "dlls"
    
    if not dll_dir.exists():
        warnings.warn(f"DLL directory not found: {dll_dir}. Extension may fail to load.", UserWarning)
        return False
    
    # Add to PATH
    dll_dir_str = str(dll_dir.absolute())
    current_path = os.environ.get('PATH', '')
    if dll_dir_str not in current_path:
        os.environ['PATH'] = dll_dir_str + os.pathsep + current_path
    
    # Use Windows DLL directory API (Python 3.8+)
    if hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(dll_dir_str)
        except (OSError, AttributeError):
            pass  # Fallback to PATH
    
    # Alternative: SetDllDirectory for older Python
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetDllDirectoryW(dll_dir_str)
    except:
        pass  # PATH method should work
    
    return True

def setup_linux_libraries(module_dir):
    """Setup Linux library loading"""
    # Check for shared libraries directory
    lib_dir = module_dir / "libs"
    
    if lib_dir.exists():
        # Add to LD_LIBRARY_PATH for shared libraries
        lib_dir_str = str(lib_dir.absolute())
        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        if lib_dir_str not in current_ld_path:
            if current_ld_path:
                os.environ['LD_LIBRARY_PATH'] = lib_dir_str + os.pathsep + current_ld_path
            else:
                os.environ['LD_LIBRARY_PATH'] = lib_dir_str
        return True
    
    # For static linking, no runtime setup needed
    return True

# Automatically setup library path when module is imported
_lib_setup_success = setup_library_search_path()

# Import the main thermal camera extension module after setting up library paths
try:
    # Import the compiled extension module directly
    import tiny_thermal_camera as _ttc_extension
    
    # Make the extension functions available directly from this package
    for attr in dir(_ttc_extension):
        if not attr.startswith('_') and not hasattr(sys.modules[__name__], attr):
            globals()[attr] = getattr(_ttc_extension, attr)
            
    # Verify key classes are available
    if not hasattr(sys.modules[__name__], 'ThermalCamera'):
        raise ImportError("ThermalCamera class not found in extension module")
    if not hasattr(sys.modules[__name__], 'TemperatureProcessor'):
        raise ImportError("TemperatureProcessor class not found in extension module")
        
    _extension_loaded = True
            
except ImportError as e:
    _extension_loaded = False
    warnings.warn(
        f"Failed to import thermal camera extension: {e}. "
        "This may be due to missing libraries, incompatible hardware, or build issues. "
        "The package is installed but camera functionality will not be available.",
        UserWarning
    )
    
    # Create dummy classes for better error messages
    class ThermalCamera:
        def __init__(self):
            raise RuntimeError("Thermal camera extension not available. Please check installation and dependencies.")
    
    class TemperatureProcessor:
        @staticmethod
        def temp_to_celsius(*args, **kwargs):
            raise RuntimeError("Thermal camera extension not available. Please check installation and dependencies.")

# Convenience functions for common operations
def get_camera_info():
    """Get information about available thermal cameras"""
    if not _extension_loaded:
        return "Extension not loaded - no camera information available"
    
    # This would be implemented in the C++ extension
    return "P2/Tiny1C thermal camera support available"

def check_dependencies():
    """Check if all required dependencies are available"""
    issues = []
    
    if not _lib_setup_success:
        issues.append("Library setup failed")
    
    if not _extension_loaded:
        issues.append("Extension module not loaded")
    
    # Check for numpy
    try:
        import numpy
    except ImportError:
        issues.append("NumPy not available")
    
    # Platform-specific checks
    system = platform.system().lower()
    if system == 'linux':
        # Check USB permissions (this is informational)
        issues.append("Note: USB permissions may need adjustment on Linux")
    
    return issues if issues else ["All dependencies appear to be available"]

# Export public API
__all__ = [
    'ThermalCamera',
    'TemperatureProcessor', 
    'get_camera_info',
    'check_dependencies',
    '__version__',
]
