#!/usr/bin/env python3
"""
Debug DLL loading issues for thermal camera
"""

import os
import sys
import ctypes
import ctypes.util
from pathlib import Path

def test_dll_loading():
    """Test loading the thermal camera DLLs directly"""
    print("=== DLL Loading Debug ===\n")
    
    # DLL locations to test
    dll_locations = [
        "./libs/win/x64/dll",
        "C:/Users/mail/anaconda3/Lib/site-packages/thermal_camera_sdk-1.0.0-py3.12-win-amd64.egg",
        "."
    ]
    
    dll_names = ["libiruvc.dll", "libirtemp.dll", "libirprocess.dll", "libirparse.dll"]
    
    for location in dll_locations:
        print(f"\n--- Testing location: {location} ---")
        if not os.path.exists(location):
            print(f"[SKIP] Directory does not exist")
            continue
            
        for dll_name in dll_names:
            dll_path = os.path.join(location, dll_name)
            print(f"\nTesting: {dll_path}")
            
            if not os.path.exists(dll_path):
                print(f"  [MISSING] File does not exist")
                continue
                
            print(f"  [EXISTS] File found")
            
            # Get file info
            stat = os.stat(dll_path)
            print(f"  [SIZE] {stat.st_size} bytes")
            
            # Try to load with ctypes
            try:
                dll = ctypes.CDLL(dll_path)
                print(f"  [SUCCESS] Loaded with ctypes.CDLL")
                
                # Try to get a function we know should exist
                if dll_name == "libiruvc.dll":
                    try:
                        func = dll.uvc_camera_init
                        print(f"  [SUCCESS] Found uvc_camera_init function")
                    except AttributeError:
                        print(f"  [WARNING] uvc_camera_init function not found")
                        
            except OSError as e:
                print(f"  [ERROR] Failed to load: {e}")
                
                # Try to get more specific error info
                try:
                    error_code = ctypes.get_last_error()
                    print(f"  [ERROR CODE] {error_code}")
                except:
                    pass

def test_python_extension():
    """Test loading the Python extension directly"""
    print("\n=== Python Extension Loading Debug ===\n")
    
    extension_paths = [
        "./tiny_thermal_camera.cp312-win_amd64.pyd",
        "C:/Users/mail/anaconda3/Lib/site-packages/thermal_camera_sdk-1.0.0-py3.12-win-amd64.egg/tiny_thermal_camera.cp312-win_amd64.pyd"
    ]
    
    for ext_path in extension_paths:
        print(f"\nTesting extension: {ext_path}")
        
        if not os.path.exists(ext_path):
            print(f"  [MISSING] Extension does not exist")
            continue
            
        print(f"  [EXISTS] Extension found")
        
        # Try loading as DLL first to see dependencies
        try:
            dll = ctypes.CDLL(ext_path)
            print(f"  [SUCCESS] Extension loaded as DLL")
        except OSError as e:
            print(f"  [ERROR] Failed to load extension as DLL: {e}")

def check_dll_dependencies():
    """Check what dependencies the DLLs have"""
    print("\n=== DLL Dependencies Check ===\n")
    
    dll_path = "./libs/win/x64/dll/libiruvc.dll"
    if os.path.exists(dll_path):
        print(f"Checking dependencies for: {dll_path}")
        
        # Use dumpbin if available
        try:
            import subprocess
            result = subprocess.run([
                "dumpbin", "/dependents", dll_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("Dependencies found:")
                print(result.stdout)
            else:
                print(f"dumpbin failed: {result.stderr}")
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("dumpbin not available")
            
        # Alternative: Try loading and see what's missing
        try:
            dll = ctypes.CDLL(dll_path)
            print("DLL loaded successfully - no missing dependencies")
        except OSError as e:
            print(f"DLL loading failed: {e}")
    else:
        print(f"DLL not found at: {dll_path}")

def test_path_methods():
    """Test different methods of setting DLL search paths"""
    print("\n=== DLL Path Methods Test ===\n")
    
    dll_dir = os.path.abspath("./libs/win/x64/dll")
    print(f"DLL directory: {dll_dir}")
    
    if not os.path.exists(dll_dir):
        print("DLL directory does not exist!")
        return
    
    # Method 1: Add to PATH
    print("\n1. Testing PATH method...")
    original_path = os.environ.get('PATH', '')
    try:
        if dll_dir not in original_path:
            os.environ['PATH'] = dll_dir + os.pathsep + original_path
            print(f"Added to PATH: {dll_dir}")
        
        # Try loading extension
        try:
            import tiny_thermal_camera
            print("SUCCESS: Extension loaded with PATH method")
        except ImportError as e:
            print(f"FAILED: {e}")
    finally:
        os.environ['PATH'] = original_path
    
    # Method 2: os.add_dll_directory (Python 3.8+)
    if hasattr(os, 'add_dll_directory'):
        print("\n2. Testing add_dll_directory method...")
        try:
            cookie = os.add_dll_directory(dll_dir)
            print(f"Added DLL directory: {dll_dir}")
            
            try:
                import tiny_thermal_camera
                print("SUCCESS: Extension loaded with add_dll_directory method")
            except ImportError as e:
                print(f"FAILED: {e}")
                
            os.remove_dll_directory(cookie)
        except Exception as e:
            print(f"add_dll_directory failed: {e}")
    
    # Method 3: SetDllDirectory
    print("\n3. Testing SetDllDirectory method...")
    try:
        kernel32 = ctypes.windll.kernel32
        result = kernel32.SetDllDirectoryW(dll_dir)
        if result:
            print(f"SetDllDirectory succeeded: {dll_dir}")
            
            try:
                import tiny_thermal_camera
                print("SUCCESS: Extension loaded with SetDllDirectory method")
            except ImportError as e:
                print(f"FAILED: {e}")
        else:
            print("SetDllDirectory failed")
            
        # Reset
        kernel32.SetDllDirectoryW(None)
    except Exception as e:
        print(f"SetDllDirectory method failed: {e}")

def main():
    """Run all debugging tests"""
    test_dll_loading()
    check_dll_dependencies() 
    test_python_extension()
    test_path_methods()

if __name__ == "__main__":
    main()