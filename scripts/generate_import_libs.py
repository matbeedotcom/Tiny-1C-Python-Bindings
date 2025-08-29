#!/usr/bin/env python3
"""
Generate import libraries (.lib) from DLLs for Windows x64
This is needed to link against the DLLs when building the Python extension
"""

import os
import shutil
import subprocess
import sys

def copy_dlls():
    """Copy 64-bit DLLs from FalconApplication"""
    source_dir = r"C:\Users\mail\dev\personal\Tiny 1c windows 上位机 FalconApplication_0.10.6\FalconApplication_0.10.6"
    target_dir = r"libs\win\x64\dll"
    
    # Create target directory
    os.makedirs(target_dir, exist_ok=True)
    
    # List of thermal camera DLLs to copy
    dll_files = [
        "libiruvc.dll",
        "libirtemp.dll",
        "libirprocess.dll",
        "libirparse.dll"
    ]
    
    for dll in dll_files:
        source = os.path.join(source_dir, dll)
        target = os.path.join(target_dir, dll)
        if os.path.exists(source):
            print(f"Copying {dll}...")
            shutil.copy2(source, target)
        else:
            print(f"Warning: {dll} not found at {source}")
    
    print(f"\nDLLs copied to {target_dir}")
    return target_dir

def generate_import_libs(dll_dir):
    """
    Generate import libraries from DLLs using Visual Studio tools
    This requires Visual Studio or Build Tools to be installed
    """
    
    # Try to find Visual Studio tools
    vs_paths = [
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
    ]
    
    dumpbin_path = None
    lib_path = None
    
    for vs_path in vs_paths:
        if os.path.exists(vs_path):
            # Find the latest version
            versions = os.listdir(vs_path)
            if versions:
                latest = sorted(versions)[-1]
                tool_dir = os.path.join(vs_path, latest, "bin", "Hostx64", "x64")
                if os.path.exists(tool_dir):
                    dumpbin_path = os.path.join(tool_dir, "dumpbin.exe")
                    lib_path = os.path.join(tool_dir, "lib.exe")
                    if os.path.exists(dumpbin_path) and os.path.exists(lib_path):
                        break
    
    if not dumpbin_path or not lib_path:
        print("Error: Visual Studio tools not found. Please install Visual Studio Build Tools.")
        print("You can manually create .lib files using:")
        print("1. dumpbin /exports <dll_file> > exports.txt")
        print("2. Create a .def file from the exports")
        print("3. lib /def:<def_file> /out:<lib_file> /machine:x64")
        return False
    
    print(f"Found Visual Studio tools at {os.path.dirname(dumpbin_path)}")
    
    # Process each DLL
    dll_files = [f for f in os.listdir(dll_dir) if f.endswith('.dll')]
    
    for dll_file in dll_files:
        dll_path = os.path.join(dll_dir, dll_file)
        lib_file = dll_file.replace('.dll', '.lib')
        lib_path = os.path.join(dll_dir, lib_file)
        def_file = dll_file.replace('.dll', '.def')
        def_path = os.path.join(dll_dir, def_file)
        
        print(f"\nProcessing {dll_file}...")
        
        # Step 1: Export symbols
        try:
            exports = subprocess.check_output([dumpbin_path, "/exports", dll_path], 
                                            stderr=subprocess.STDOUT, text=True)
            
            # Parse exports and create DEF file
            lines = exports.split('\n')
            in_exports = False
            symbols = []
            
            for line in lines:
                if 'ordinal hint' in line.lower():
                    in_exports = True
                    continue
                if in_exports and line.strip():
                    parts = line.split()
                    if len(parts) >= 4 and parts[0].isdigit():
                        # Extract symbol name (4th column typically)
                        symbol = parts[3] if len(parts) > 3 else None
                        if symbol and not symbol.startswith('?'):  # Skip mangled C++ names
                            symbols.append(symbol)
            
            if symbols:
                # Create DEF file
                with open(def_path, 'w') as f:
                    f.write(f"LIBRARY {dll_file}\n")
                    f.write("EXPORTS\n")
                    for symbol in symbols:
                        f.write(f"    {symbol}\n")
                
                print(f"  Created {def_file} with {len(symbols)} exports")
                
                # Step 2: Generate import library
                result = subprocess.run([lib_path, f"/def:{def_path}", f"/out:{lib_path}", "/machine:x64"],
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"  Generated {lib_file}")
                    # Clean up DEF file
                    os.remove(def_path)
                else:
                    print(f"  Error generating lib: {result.stderr}")
            else:
                print(f"  Warning: No exports found in {dll_file}")
                
        except subprocess.CalledProcessError as e:
            print(f"  Error processing {dll_file}: {e}")
        except Exception as e:
            print(f"  Unexpected error: {e}")
    
    return True

def main():
    print("=== Generating Import Libraries for x64 DLLs ===\n")
    
    # Copy DLLs
    dll_dir = copy_dlls()
    
    # Generate import libraries
    print("\n=== Generating Import Libraries ===")
    if generate_import_libs(dll_dir):
        print("\n=== Success! ===")
        print(f"DLLs and import libraries are ready in {dll_dir}")
        print("\nYou can now build the Python extension with:")
        print("  python setup_crossplatform.py build_ext --inplace")
    else:
        print("\n=== Manual Steps Required ===")
        print("Please generate the .lib files manually or use a different approach.")

if __name__ == "__main__":
    main()