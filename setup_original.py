#!/usr/bin/env python3

from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
import subprocess
import os

def get_opencv_flags():
    """Get OpenCV compiler and linker flags"""
    try:
        cflags = subprocess.check_output(['pkg-config', 'opencv4', '--cflags']).decode('utf-8').strip().split()
        libs = subprocess.check_output(['pkg-config', 'opencv4', '--libs']).decode('utf-8').strip().split()
        return cflags, libs
    except:
        # Fallback to manual paths
        return ['-I/usr/include/opencv4'], ['-lopencv_core', '-lopencv_imgproc', '-lopencv_highgui', '-lopencv_imgcodecs']

opencv_cflags, opencv_libs = get_opencv_flags()

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "thermal_camera",
        sources=[
            "python_bindings.cpp",
            "camera.cpp",
            "temperature.cpp",
            "data.cpp",
            "display.cpp",
            "cmd.cpp",
        ],
        include_dirs=[
            # Path to pybind11 headers
            pybind11.get_include(),
            # Local include directory
            "./include",
            ".",
        ] + [flag[2:] for flag in opencv_cflags if flag.startswith('-I')],  # Extract -I paths
        
        libraries=[
            "iruvc", "irtemp", "irprocess", "irparse", "pthread", "m"
        ],
        
        library_dirs=[
            "./libs/linux/x86-linux_libs",
        ],
        
        runtime_library_dirs=[
            "./libs/linux/x86-linux_libs",
        ],
        
        language='c++',
        cxx_std=11,
        
        define_macros=[
            ("IMAGE_AND_TEMP_OUTPUT", None),  # Enable both image and temperature output
        ],
        
        extra_compile_args=[
            "-O3",
            "-Wall",
        ] + [flag for flag in opencv_cflags if not flag.startswith('-I')],
        
        extra_link_args=[
            "-Wl,-rpath,./libs/linux/x86-linux_libs",
        ] + opencv_libs,
    ),
]

setup(
    name="thermal_camera",
    version="1.0.0",
    author="Thermal Camera Python Bindings",
    author_email="",
    description="Python bindings for P2/Tiny1C thermal camera SDK",
    long_description="""
    Python bindings for the AC010_256 thermal camera SDK.
    Supports P2/Tiny1C thermal cameras with temperature measurement capabilities.
    
    Features:
    - Camera control (open/close, start/stop streaming)
    - Real-time temperature frame acquisition
    - Point, line, and area temperature measurement
    - NumPy array integration for easy data processing
    """,
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.15.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)