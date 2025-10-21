@echo off
REM Quick launcher for Windows setup
REM Redirects to the actual setup script in tools/

echo.
echo Starting Thermal Camera Setup...
echo.

if exist tools\SETUP_WINDOWS.bat (
    call tools\SETUP_WINDOWS.bat
) else (
    echo ERROR: Setup script not found at tools\SETUP_WINDOWS.bat
    echo Please ensure you're running this from the project root directory.
    pause
    exit /b 1
)
