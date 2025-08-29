"""
Thermal Camera SDK - Cross-platform library loader
This module ensures libraries are found at runtime on all platforms
"""

import os
import sys
import platform
from pathlib import Path

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
setup_library_search_path()

# Import the main thermal camera extension module after setting up library paths
try:
    # Import the compiled extension module by name from the installed location
    import importlib.util
    import sys
    
    # Try to find the extension module in the site-packages or current directory
    try:
        # Try importing from site-packages first
        from . import tiny_thermal_camera as _ttc_extension
    except ImportError:
        # If that fails, try importing from the global namespace
        import tiny_thermal_camera as _ttc_extension
    
    # Make the extension functions available directly from this package
    for attr in dir(_ttc_extension):
        if not attr.startswith('_') and not hasattr(sys.modules[__name__], attr):
            globals()[attr] = getattr(_ttc_extension, attr)
            
except ImportError as e:
    # If import fails, it's likely due to missing libraries or hardware
    pass
