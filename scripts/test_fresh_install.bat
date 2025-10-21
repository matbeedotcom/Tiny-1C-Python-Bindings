@echo off
REM Test the wheel as a fresh user would install it

echo ========================================
echo Testing Fresh User Installation
echo ========================================
echo.
echo This test will:
echo   1. Create a fresh virtual environment
echo   2. Install the wheel from wheelhouse/
echo   3. Test importing and using the module
echo   4. Verify all DLLs are bundled (including msvcr100.dll)
echo.

if "%1"=="" (
    echo No wheel path specified, will use latest from wheelhouse/
    python scripts\test_fresh_install.py
) else (
    echo Using wheel: %1
    python scripts\test_fresh_install.py "%1"
)

if errorlevel 1 (
    echo.
    echo ========================================
    echo FAILED: Fresh install test failed
    echo ========================================
    exit /b 1
) else (
    echo.
    echo ========================================
    echo SUCCESS: Wheel works for fresh users!
    echo ========================================
)
