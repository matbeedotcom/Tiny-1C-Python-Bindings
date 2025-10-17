#!/usr/bin/env python3
"""
Cross-platform setup script for Tiny Thermal Camera Python bindings
Supports Windows, Linux (x86, ARM, MIPS), and cross-compilation
"""

from setuptools import setup, Extension, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11
import subprocess
import platform
import sys
import os
import shutil
from pathlib import Path

def get_platform_info():
    """Detect platform and architecture"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Check for cross-compilation environment variables
    cross_compile = os.environ.get('CROSS_COMPILE', '')
    target_arch = os.environ.get('TARGET_ARCH', '')
    
    if cross_compile:
        return 'linux', target_arch or cross_compile.split('-')[0]
    
    return system, machine

def get_linux_lib_path(arch, cross_compile=''):
    """Determine the correct Linux library path based on architecture"""
    lib_base = "./libs/linux/"
    
    # Map architectures to library directories
    arch_map = {
        # x86 architectures
        'x86_64': 'x86-linux_libs',
        'x86': 'x86-linux_libs',
        'i686': 'x86-linux_libs',
        'i386': 'x86-linux_libs',
        
        # ARM 64-bit architectures
        'aarch64': 'aarch64-linux-gnu_libs',
        'arm64': 'aarch64-linux-gnu_libs',
        
        # ARM 32-bit architectures
        'armv7l': 'arm-linux-gnueabihf_libs',
        'armv7': 'arm-linux-gnueabihf_libs',
        'armv6l': 'arm-linux-gnueabi_libs',
        'arm': 'arm-linux-gnueabi_libs',
        
        # MIPS architectures
        'mips': 'mips-linux-gnu_libs',
        'mipsel': 'mips-linux-gnu_libs',
    }
    
    # Special cross-compilation targets
    cross_compile_map = {
        'aarch64-linux-gnu': 'aarch64-linux-gnu_libs',
        'aarch64-none-linux-gnu': 'aarch64-none-linux-gnu_libs',
        'aarch64-v01c01-linux-musl': 'aarch64-v01c01-linux-musl_libs',
        'arm-buildroot-linux-uclibcgnueabihf': 'arm-buildroot-linux-uclibcgnueabihf_libs',
        'arm-himix100-linux': 'arm-himix100-linux_libs',
        'arm-himix200-linux': 'arm-himix200-linux_libs',
        'arm-hisiv300-linux-uclibcgnueabi': 'arm-hisiv300-linux-uclibcgnueabi_libs',
        'arm-hisiv500-linux-uclibcgnueabi': 'arm-hisiv500-linux-uclibcgnueabi_libs',
        'arm-linux-gnueabi': 'arm-linux-gnueabi_libs',
        'arm-linux-gnueabihf': 'arm-linux-gnueabihf_libs',
        'mips-linux-gnu': 'mips-linux-gnu_libs',
    }
    
    # Check for specific cross-compilation target
    if cross_compile and cross_compile in cross_compile_map:
        return lib_base + cross_compile_map[cross_compile]
    
    # Fallback to architecture mapping
    lib_dir = arch_map.get(arch, 'x86-linux_libs')
    lib_path = lib_base + lib_dir
    
    # Verify the path exists
    if not os.path.exists(lib_path):
        print(f"Warning: Library path {lib_path} not found, defaulting to x86-linux_libs")
        lib_path = lib_base + "x86-linux_libs"
    
    return lib_path

def get_opencv_flags(system):
    """Get OpenCV compiler and linker flags for the platform"""
    # First check if local OpenCV headers exist
    local_opencv = "./libir_sample"
    if os.path.exists(local_opencv):
        print(f"Using local OpenCV headers from {local_opencv}")
        # Just return the include path, no libraries needed for basic functionality
        return [local_opencv], []
    
    if system == 'windows':
        # Windows OpenCV paths (adjust as needed)
        opencv_include = os.environ.get('OPENCV_INCLUDE', './libir_sample')
        opencv_lib = os.environ.get('OPENCV_LIB', '')
        
        # Check if OpenCV library is specified and exists
        if opencv_lib:
            opencv_lib_file = os.path.join(opencv_lib, 'opencv_world.lib')
            if os.path.exists(opencv_lib_file):
                return [opencv_include], [opencv_lib_file]
        
        # Just use headers without linking to OpenCV libs
        print(f"Using OpenCV headers only from {opencv_include}")
        return [opencv_include], []
    else:
        # Linux/Unix - use pkg-config
        try:
            cflags = subprocess.check_output(['pkg-config', 'opencv4', '--cflags']).decode('utf-8').strip().split()
            libs = subprocess.check_output(['pkg-config', 'opencv4', '--libs']).decode('utf-8').strip().split()
            return cflags, libs
        except:
            # Fallback to local headers
            print(f"Warning: OpenCV not found via pkg-config, using local headers from {local_opencv}")
            return [local_opencv], []

def create_extension(system, arch):
    """Create platform-specific extension configuration"""
    
    opencv_cflags, opencv_libs = get_opencv_flags(system)
    cross_compile = os.environ.get('CROSS_COMPILE', '')
    
    # Base configuration
    include_dirs = [
        pybind11.get_include(),
        "./include",
        "./libs/include",  # Additional include path
        ".",
    ]
    
    libraries = []
    extra_objects = []
    extra_compile_args = []
    extra_link_args = []
    define_macros = [("IMAGE_AND_TEMP_OUTPUT", None)]
    
    if system == 'windows':
        # Windows configuration - detect architecture
        import platform
        is_64bit = platform.machine().endswith('64')
        
        if is_64bit:
            # Use x64 DLLs from FalconApplication
            lib_path = os.path.abspath("./libs/win/x64/dll")
            
            # Check if we have the x64 DLLs and import libraries
            if os.path.exists(lib_path):
                # Use import libraries for linking
                lib_files = ["libiruvc.lib", "libirtemp.lib", "libirprocess.lib", "libirparse.lib"]
                for lib_file in lib_files:
                    lib_file_path = os.path.join(lib_path, lib_file)
                    if os.path.exists(lib_file_path):
                        extra_objects.append(lib_file_path)
                    else:
                        print(f"Warning: {lib_file} not found")
                print(f"Using 64-bit DLLs and import libraries from {lib_path}")
            else:
                print("Warning: x64 DLLs not found, build may fail")
        else:
            # Use Win32 libraries for 32-bit Python
            lib_base_path = "./libs/win/Win32/"
            use_dll = os.environ.get('USE_DLL', '1') == '1'
            
            if use_dll:
                lib_path = os.path.abspath(lib_base_path + "dll")
                extra_objects.extend([
                    os.path.join(lib_path, "libiruvc.lib"),
                    os.path.join(lib_path, "libirtemp.lib"),
                    os.path.join(lib_path, "libirprocess.lib"),
                    os.path.join(lib_path, "libirparse.lib"),
                ])
            else:
                lib_path = os.path.abspath(lib_base_path + "lib")
                extra_objects.extend([
                    os.path.join(lib_path, "libiruvc.lib"),
                    os.path.join(lib_path, "libirtemp.lib"),
                    os.path.join(lib_path, "libirprocess.lib"),
                    os.path.join(lib_path, "libirparse.lib"),
                ])
        
        # Windows system libraries
        libraries.extend(['ws2_32', 'winusb', 'setupapi'])
        define_macros.append(("WIN32", None))
        define_macros.append(("_WINDOWS", None))
        
        # MSVC compiler flags
        extra_compile_args.extend(['/O2', '/MD'])
        
    else:  # Linux/Unix
        lib_path = get_linux_lib_path(arch, cross_compile)
        
        # Check if we should use shared or static libraries
        use_shared = os.environ.get('USE_SHARED', '0') == '1'
        
        if use_shared:
            # Use shared libraries
            libraries.extend(['iruvc', 'irtemp', 'irprocess', 'irparse'])
            extra_link_args.extend([f'-L{os.path.abspath(lib_path)}', f'-Wl,-rpath,$ORIGIN/{lib_path}'])
        else:
            # Use static libraries (default)
            lib_files = ['libiruvc', 'libirtemp', 'libirprocess', 'libirparse']

            # Check for MIPS (limited libraries)
            if 'mips' in lib_path:
                lib_files = ['libirtemp', 'libirprocess', 'libirparse']  # No libiruvc for MIPS

            for lib in lib_files:
                lib_file = f"{lib_path}/{lib}.a"
                if os.path.exists(lib_file):
                    extra_objects.append(lib_file)
                else:
                    print(f"Warning: {lib_file} not found")

        # Use system libusb-1.0 (auditwheel will bundle it into the wheel)
        # Note: bundled libusb-1.0.a is not compiled with -fPIC and cannot be used
        libraries.append('usb-1.0')

        # Linux system libraries (pthread and math)
        libraries.extend(['pthread', 'm'])
        define_macros.append(("linux", None))
        
        # GCC compiler flags
        extra_compile_args.extend(['-O3', '-Wall', '-fPIC'])
        
        # Add cross-compilation flags if needed
        if cross_compile:
            extra_compile_args.append(f'--target={cross_compile}')
            extra_link_args.append(f'--target={cross_compile}')
    
    # Add OpenCV flags
    if system == 'windows':
        # For Windows, opencv_cflags is just a list with the include path
        include_dirs.extend(opencv_cflags)
        # opencv_libs contains the .lib file path
        extra_objects.extend(opencv_libs)
    else:
        # For Linux, parse the flags properly
        include_dirs.extend([flag[2:] for flag in opencv_cflags if flag.startswith('-I')])
        extra_compile_args.extend([flag for flag in opencv_cflags if not flag.startswith('-I')])
        extra_link_args.extend(opencv_libs)
    
    # Create extension
    return Pybind11Extension(
        "tiny_thermal_camera",
        sources=["python_bindings_tiny.cpp"],
        include_dirs=include_dirs,
        libraries=libraries,
        extra_objects=extra_objects,
        language='c++',
        cxx_std=11,
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )

# Detect platform and create extension (runs on module import)
system, arch = get_platform_info()
cross_compile = os.environ.get('CROSS_COMPILE', '')

print(f"Building for: {system} / {arch}")
if cross_compile:
    print(f"Cross-compiling for: {cross_compile}")

# Create extension module
ext_modules = [create_extension(system, arch)]

# Run setup - metadata comes from pyproject.toml
# This runs when the module is imported by setuptools.build_meta
# Note: Windows DLL bundling is handled by delvewheel during the repair step
setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)