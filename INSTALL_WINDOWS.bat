@echo off
REM NeoCompression Windows Installation Script
REM This script handles installation on Windows without requiring PATH modifications

echo ============================================
echo NeoCompression Windows Installer
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.10 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Found Python installation...
python --version
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%"

echo Installing NeoCompression...
echo.

REM Install using pip with full path to avoid issues
python -m pip install --upgrade pip
python -m pip install .

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed.
    echo Please ensure you have internet connectivity and try again.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Installation complete!
echo ============================================
echo.
echo You can now use NeoCompression in two ways:
echo.
echo 1. GUI Mode (Recommended):
echo    neocompression
echo.
echo 2. Command Line:
echo    neocompression compress "folder" archive.neo
echo    neocompression decompress archive.neo output
echo.
echo 3. Short commands:
echo    neo c "folder" archive.neo
echo    neo x archive.neo output
echo.
echo Press any key to test the installation...
pause >nul

echo.
echo Testing installation...
neocompression --help

echo.
echo If you see the help text above, installation was successful!
echo.
pause