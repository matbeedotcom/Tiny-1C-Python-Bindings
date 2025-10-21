@echo off
REM Build and test wheel repair for Windows
REM This script builds a wheel locally and verifies DLL bundling

echo ========================================
echo Building and Testing Windows Wheel
echo ========================================

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist wheelhouse rmdir /s /q wheelhouse
if exist *.egg-info rmdir /s /q *.egg-info

REM Install build dependencies
echo.
echo Installing build dependencies...
python -m pip install --upgrade pip build wheel setuptools pybind11 numpy delvewheel

REM Temporarily remove DLLs from src (delvewheel will bundle them)
echo.
echo Temporarily moving DLLs out of source tree...
if exist src\tiny_thermal_camera\dlls_backup rmdir /s /q src\tiny_thermal_camera\dlls_backup
if exist src\tiny_thermal_camera\dlls (
    move src\tiny_thermal_camera\dlls src\tiny_thermal_camera\dlls_backup
)

REM Build the wheel
echo.
echo Building wheel...
python -m build --wheel

REM Restore DLLs for development
echo.
echo Restoring DLLs for development...
if exist src\tiny_thermal_camera\dlls_backup (
    move src\tiny_thermal_camera\dlls_backup src\tiny_thermal_camera\dlls
)

REM Check if wheel was created
if not exist dist\*.whl (
    echo ERROR: No wheel was created!
    exit /b 1
)

REM Create wheelhouse directory and copy wheel
if not exist wheelhouse mkdir wheelhouse
copy dist\*.whl wheelhouse\

REM Repair the wheel with delvewheel
echo.
echo Repairing wheel with delvewheel...
for %%f in (dist\*.whl) do (
    echo Repairing: %%f
    delvewheel repair --add-path libs/win/x64/dll -w wheelhouse "%%f"
    if errorlevel 1 (
        echo ERROR: delvewheel repair failed!
        exit /b 1
    )
)

REM Test the repaired wheel
echo.
echo Testing repaired wheel...
python scripts\test_wheel_repair.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo FAILED: Wheel repair verification failed
    echo ========================================
    exit /b 1
) else (
    echo.
    echo ========================================
    echo SUCCESS: Wheel is properly repaired!
    echo ========================================
    echo.
    echo Repaired wheel is in: wheelhouse\
    dir /b wheelhouse\*.whl
)
