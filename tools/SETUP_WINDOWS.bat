@echo off
REM First-Time Setup for Thermal Camera on Windows
REM This batch file automates the entire setup process

echo.
echo ======================================================================
echo   Thermal Camera Setup for Windows
echo   Tiny1C / AC010_256 Series
echo ======================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check if the package is built
echo Checking if tiny_thermal_camera package is available...
python -c "import tiny_thermal_camera" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Package not built yet
    echo.
    echo Would you like to build it now? (Requires Visual C++ Build Tools)
    echo.
    set /p BUILD="Build now? (y/n): "
    if /i "%BUILD%"=="y" (
        echo.
        echo Building package...
        call build_windows.bat
        if errorlevel 1 (
            echo [ERROR] Build failed
            echo.
            echo Make sure you have Visual C++ Build Tools installed:
            echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Setup cannot continue without the package built
        echo Please run: build_windows.bat
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Package is available
echo.

REM Run the setup wizard
echo Launching setup wizard...
echo.
python setup_camera.py

echo.
echo ======================================================================
echo   Setup script completed
echo ======================================================================
echo.
pause
