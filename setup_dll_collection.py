#!/usr/bin/env python3
"""
Script to collect all required DLLs for the thermal camera package
"""

import os
import shutil
import platform
from pathlib import Path

def collect_windows_dlls():
    """Collect all Windows DLLs needed for the thermal camera"""
    print("=== Collecting Windows DLLs ===")
    
    # Determine architecture
    is_64bit = platform.machine().endswith('64')
    arch_dir = 'x64' if is_64bit else 'Win32'
    
    # Source and destination paths
    source_base = Path("libs/win")
    dest_dir = Path("tiny_thermal_camera/dlls")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Target architecture: {arch_dir}")
    print(f"Destination: {dest_dir}")
    
    # Core thermal camera DLLs
    thermal_dlls = [
        "libiruvc.dll",
        "libirtemp.dll", 
        "libirprocess.dll",
        "libirparse.dll"
    ]
    
    # Runtime dependencies (these are the ones we identified as missing)
    runtime_dlls = [
        "pthreadVC2.dll",
        "msvcp140.dll",
        "vcruntime140.dll",
        "vcruntime140_1.dll"
    ]
    
    all_dlls = thermal_dlls + runtime_dlls
    
    copied_files = []
    
    # Copy from the x64/dll directory (which has both thermal and runtime DLLs)
    source_dir = source_base / arch_dir / "dll"
    
    if source_dir.exists():
        print(f"\nCopying from: {source_dir}")
        
        for dll_name in all_dlls:
            source_file = source_dir / dll_name
            dest_file = dest_dir / dll_name
            
            if source_file.exists():
                shutil.copy2(source_file, dest_file)
                print(f"  [OK] {dll_name}")
                copied_files.append(dll_name)
            else:
                print(f"  [MISSING] {dll_name} - NOT FOUND")
    
    # Also copy import libraries for linking
    lib_dest_dir = Path("tiny_thermal_camera/libs")
    lib_dest_dir.mkdir(parents=True, exist_ok=True)
    
    for dll_name in thermal_dlls:
        lib_name = dll_name.replace('.dll', '.lib')
        source_lib = source_dir / lib_name
        dest_lib = lib_dest_dir / lib_name
        
        if source_lib.exists():
            shutil.copy2(source_lib, dest_lib)
            print(f"  [OK] {lib_name} (import library)")
    
    print(f"\nCopied {len(copied_files)} DLL files to {dest_dir}")
    return list(dest_dir.glob("*.dll"))


def main():
    """Main collection function"""
    if platform.system().lower() != 'windows':
        print("DLL collection is only needed on Windows")
        return
    
    # Clean up previous DLL collections (but keep __init__.py)
    dll_dir = Path("tiny_thermal_camera/dlls")
    lib_dir = Path("tiny_thermal_camera/libs")
    if dll_dir.exists():
        shutil.rmtree(dll_dir)
    if lib_dir.exists():
        shutil.rmtree(lib_dir)
    
    # Collect DLLs
    dll_files = collect_windows_dlls()
    
    print(f"\n=== Collection Complete ===")
    print(f"[SUCCESS] {len(dll_files)} DLLs ready for packaging")
    print("Note: tiny_thermal_camera/__init__.py already exists for DLL loading")
    print("Next: Update setup.py to include tiny_thermal_camera package")

if __name__ == "__main__":
    main()