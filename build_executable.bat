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
echo Generating version info file...
python generate_version_info.py
if errorlevel 1 (
    echo ERROR: Failed to generate version info!
    pause
    exit /b 1
)

echo.
echo Building executable with PyInstaller...
echo This may take a few minutes...
echo.

REM Check if icon file exists
if exist "icon.ico" (
    echo Using custom icon: icon.ico
) else (
    echo No icon file found. Building without custom icon.
    echo To add an icon, place icon.ico in the project root directory.
)

REM Build with console enabled but hidden late (for CLI support)
python -m PyInstaller --clean --noconfirm ^
    --name=BRLibToHelp ^
    --onefile ^
    --console ^
    --hide-console hide-late ^
    --add-data "css;css" ^
    --add-data "bin;bin" ^
    --add-data "version.py;." ^
    --add-data "icon.ico;." ^
    --icon=icon.ico ^
    --version-file=version_info.txt ^
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
