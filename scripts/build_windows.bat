@echo off
REM Build script for Windows - Tiny Thermal Camera Python Bindings

echo ============================================
echo Building Tiny Thermal Camera for Windows
echo ============================================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Set OpenCV paths if not already set
if "%OPENCV_INCLUDE%"=="" (
    echo Setting default OpenCV paths...
    set OPENCV_INCLUDE=C:\opencv\include
    set OPENCV_LIB=C:\opencv\x64\vc15\lib
    echo OPENCV_INCLUDE=%OPENCV_INCLUDE%
    echo OPENCV_LIB=%OPENCV_LIB%
)

REM Choose between DLL and static library
if "%1"=="static" (
    echo Using static libraries...
    set USE_DLL=0
) else (
    echo Using DLL libraries...
    set USE_DLL=1
)

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install --upgrade pip
pip install pybind11 numpy setuptools wheel

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info
del /q tiny_thermal_camera*.pyd 2>nul

REM Change to parent directory for build
cd ..

REM Build the extension
echo.
echo Building extension module...
python setup_crossplatform.py build_ext --inplace

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    exit /b 1
)

REM Copy DLLs if using dynamic linking
if "%USE_DLL%"=="1" (
    echo.
    echo Copying DLL files...
    copy libs\win\Win32\dll\*.dll . >nul 2>&1
)

echo.
echo ============================================
echo Build completed successfully!
echo ============================================
echo.
echo To test the installation, run:
echo   python tests/test_simple.py
echo.
echo To install system-wide:
echo   python setup_crossplatform.py install
echo.