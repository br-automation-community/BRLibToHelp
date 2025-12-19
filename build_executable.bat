@echo off
REM Build script for BRLibToHelp executable
REM This script creates the executable using PyInstaller

echo ========================================
echo Building BRLibToHelp Executable
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found at .venv
    echo Please create a virtual environment first.
    pause
    exit /b 1
)

REM Activate virtual environment and build
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Checking PyInstaller installation...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

echo.
echo Building executable with PyInstaller...
echo This may take a few minutes...
echo.

REM Check if icon file exists and prepare parameters
set ICON_PARAM=
set ADD_ICON_DATA=
if exist "icon.ico" (
    echo Using custom icon: icon.ico
    set ICON_PARAM=--icon=icon.ico
    set ADD_ICON_DATA=--add-data "icon.ico;."
) else (
    echo No icon file found. Building without custom icon.
    echo To add an icon, place icon.ico in the project root directory.
)

python -m PyInstaller --clean --noconfirm ^
    --name=BRLibToHelp ^
    --onefile ^
    --windowed ^
    --add-data "css;css" ^
    --add-data "bin;bin" ^
    %ADD_ICON_DATA% ^
    %ICON_PARAM% ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\BRLibToHelp.exe
echo.
echo You can now distribute the executable from the dist folder.
echo.
pause
