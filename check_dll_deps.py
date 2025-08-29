#!/usr/bin/env python3
"""
Check DLL dependencies using Python
"""

import os
import struct
import ctypes
from ctypes import wintypes

def get_dll_imports(dll_path):
    """Extract imported DLLs from a PE file"""
    try:
        with open(dll_path, 'rb') as f:
            # Read DOS header
            dos_header = f.read(64)
            if dos_header[:2] != b'MZ':
                print("Not a valid PE file")
                return []
            
            # Get PE header offset
            pe_offset = struct.unpack('<I', dos_header[60:64])[0]
            f.seek(pe_offset)
            
            # Read PE signature
            pe_sig = f.read(4)
            if pe_sig != b'PE\x00\x00':
                print("Invalid PE signature")
                return []
            
            # Read COFF header
            f.read(20)  # Skip COFF header
            
            # Read optional header size
            opt_header_size = struct.unpack('<H', f.read(2))[0]
            f.seek(-2, 1)  # Go back
            
            # Read optional header
            opt_header = f.read(opt_header_size)
            if len(opt_header) < 96:
                print("Optional header too short")
                return []
            
            # Get import table RVA and size
            import_table_rva = struct.unpack('<I', opt_header[88:92])[0]
            import_table_size = struct.unpack('<I', opt_header[92:96])[0]
            
            if import_table_rva == 0:
                print("No import table")
                return []
            
            print(f"Import table RVA: 0x{import_table_rva:x}, Size: {import_table_size}")
            
            # This is a simplified approach - finding import table in a PE file 
            # is complex and would require proper PE parsing
            
    except Exception as e:
        print(f"Error analyzing PE file: {e}")
        return []

def check_common_dependencies():
    """Check for common DLL dependencies that might be missing"""
    print("\n=== Checking Common Dependencies ===\n")
    
    # Common dependencies that thermal camera DLLs might need
    common_deps = [
        'msvcr120.dll',    # Visual C++ 2013 runtime
        'msvcp120.dll',    # Visual C++ 2013 runtime  
        'msvcr140.dll',    # Visual C++ 2015-2022 runtime
        'msvcp140.dll',    # Visual C++ 2015-2022 runtime
        'vcruntime140.dll', # Visual C++ 2015-2022 runtime
        'vcruntime140_1.dll', # Visual C++ 2015-2022 runtime
        'libusb-1.0.dll',  # USB library
        'pthreadVC2.dll',  # pthread library
        'kernel32.dll',    # System
        'user32.dll',      # System
        'advapi32.dll',    # System
        'ws2_32.dll',      # Winsock
        'winusb.dll',      # Windows USB
        'setupapi.dll',    # Setup API
    ]
    
    for dll_name in common_deps:
        try:
            # Try to load the DLL
            dll = ctypes.CDLL(dll_name)
            print(f"[OK] {dll_name} - Available")
        except OSError:
            # Try to find it in system paths
            dll_path = ctypes.util.find_library(dll_name.replace('.dll', ''))
            if dll_path:
                print(f"[OK] {dll_name} - Found at {dll_path}")
            else:
                print(f"[MISSING] {dll_name} - Not found")

def check_falcon_app_deps():
    """Check what dependencies the original FalconApplication has"""
    print("\n=== Checking FalconApplication Dependencies ===\n")
    
    falcon_dir = r"C:\Users\mail\dev\personal\Tiny 1c windows 上位机 FalconApplication_0.10.6\FalconApplication_0.10.6"
    
    if not os.path.exists(falcon_dir):
        print("FalconApplication directory not found")
        return
    
    # List all DLLs in the FalconApplication directory
    dll_files = [f for f in os.listdir(falcon_dir) if f.endswith('.dll')]
    
    print("DLLs found in FalconApplication:")
    for dll in sorted(dll_files):
        dll_path = os.path.join(falcon_dir, dll)
        size = os.path.getsize(dll_path)
        print(f"  {dll} ({size:,} bytes)")
        
        # Try to load each DLL to see which ones work
        try:
            ctypes.CDLL(dll_path)
            print(f"    [CAN LOAD] {dll}")
        except OSError as e:
            print(f"    [CANNOT LOAD] {dll}: {e}")

def test_with_falcon_path():
    """Test loading our thermal DLLs with FalconApplication in PATH"""
    print("\n=== Testing with FalconApplication in PATH ===\n")
    
    falcon_dir = r"C:\Users\mail\dev\personal\Tiny 1c windows 上位机 FalconApplication_0.10.6\FalconApplication_0.10.6"
    
    if not os.path.exists(falcon_dir):
        print("FalconApplication directory not found")
        return
    
    # Add FalconApplication to PATH
    original_path = os.environ.get('PATH', '')
    try:
        os.environ['PATH'] = falcon_dir + os.pathsep + original_path
        print(f"Added to PATH: {falcon_dir}")
        
        # Now try loading our problematic DLL
        dll_path = "./libs/win/x64/dll/libiruvc.dll"
        try:
            dll = ctypes.CDLL(dll_path)
            print(f"[SUCCESS] libiruvc.dll loaded with FalconApplication in PATH!")
            
            # Test importing the Python extension
            try:
                import tiny_thermal_camera
                print(f"[SUCCESS] Python extension loaded!")
            except ImportError as e:
                print(f"[FAILED] Python extension still failed: {e}")
                
        except OSError as e:
            print(f"[FAILED] libiruvc.dll still cannot load: {e}")
            
    finally:
        os.environ['PATH'] = original_path

def main():
    """Run dependency analysis"""
    print("=== DLL Dependency Analysis ===")
    
    dll_path = "./libs/win/x64/dll/libiruvc.dll"
    if os.path.exists(dll_path):
        print(f"\nAnalyzing: {dll_path}")
        get_dll_imports(dll_path)
    
    check_common_dependencies()
    check_falcon_app_deps()
    test_with_falcon_path()

if __name__ == "__main__":
    main()