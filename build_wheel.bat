@echo off
REM Build wheel for local testing on Windows

setlocal

echo ========================================
echo Building Wheel for Windows
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

REM Display Python version and architecture
echo Python version:
python --version
python -c "import platform; print(f'Architecture: {platform.machine()}')"
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info
if exist src\*.egg-info rmdir /s /q src\*.egg-info
echo.

REM Install build dependencies
echo Installing build dependencies...
python -m pip install --upgrade pip setuptools wheel build cibuildwheel delvewheel
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo.

REM Choose build method
echo Select build method:
echo 1. Quick build (current Python only)
echo 2. Full build (all Python versions 3.8-3.12 using cibuildwheel)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Building wheel for current Python version...
    python -m build --wheel
    if errorlevel 1 (
        echo ERROR: Build failed
        exit /b 1
    )
    echo.
    echo ========================================
    echo Wheel built successfully!
    echo Location: dist\
    dir /b dist\*.whl
    echo ========================================
) else if "%choice%"=="2" (
    echo.
    echo Building wheels for Python 3.8-3.12...
    echo This will take several minutes...
    echo.
    python -m cibuildwheel --platform windows --output-dir dist
    if errorlevel 1 (
        echo ERROR: Build failed
        exit /b 1
    )
    echo.
    echo ========================================
    echo Wheels built successfully!
    echo Location: dist\
    dir /b dist\*.whl
    echo ========================================
) else (
    echo Invalid choice. Please run again and select 1 or 2.
    exit /b 1
)

echo.
echo To install the wheel:
echo   pip install dist\[wheel-name].whl
echo.
echo To test the package:
echo   python -c "import tiny_thermal_camera; print('Success!')"
echo.

endlocal
