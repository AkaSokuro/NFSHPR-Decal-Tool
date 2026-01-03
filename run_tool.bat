@echo off
setlocal enabledelayedexpansion

title NFS:HPR Decal Tool Launcher

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Python is not installed or not in PATH!
    echo ============================================================
    echo.
    echo Please install Python 3.6 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo           NFS:HPR DECAL MODDING TOOL LAUNCHER
echo ============================================================
echo.
for /f "tokens=*" %%i in ('python --version') do echo Python: %%i
echo.

echo.
echo Checking required packages...
echo.

set MISSING_PACKAGES=0

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Pillow - NOT INSTALLED
    set MISSING_PACKAGES=1
) else (
    echo Pillow - INSTALLED
)

python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo NumPy - NOT INSTALLED
    set MISSING_PACKAGES=1
) else (
    echo NumPy - INSTALLED
)

echo.
echo Checking optional tools...
echo.

if exist "texconv.exe" (
    echo DirectXTex - INSTALLED
) else (
    echo DirectXTex - NOT FOUND
	echo ^> This is used for Image Conversion/Generation
    echo.
    set /p DOWNLOAD_TEXCONV="Do you want to download DirectXTex? (Y/N): "
    
    if /i "!DOWNLOAD_TEXCONV!"=="Y" (
        echo.
        echo Downloading DirectXTex...
        echo.
        
        powershell -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/microsoft/DirectXTex/releases/download/oct2025/texconv.exe' -OutFile 'texconv.exe'; Write-Host '[OK] DirectXTex downloaded successfully' } catch { Write-Host '[ERROR] Failed to download DirectXTex'; exit 1 }"
        
        if errorlevel 1 (
            echo.
            echo Failed to download DirectXTex automatically.
            echo.
            echo Please download manually from:
            echo https://github.com/microsoft/DirectXTex/releases/
            echo.
            echo Place it in the same folder as this batch file.
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Skipping DirectXTex download.
        echo.
        echo WARNING: Some features may not work without DirectXTex
        echo.
        timeout /t 3 >nul
    )
)

echo.
echo ============================================================

if !MISSING_PACKAGES! equ 1 (
    echo.
    echo Some required packages are missing.
    echo.
    set /p INSTALL="Do you want to install them now? (Y/N): "
    
    if /i "!INSTALL!"=="Y" (
        echo.
        echo.
        echo Installing missing packages...
        echo.
        echo.
        
        python -c "import PIL" >nul 2>&1
        if errorlevel 1 (
            echo Installing Pillow...
            python -m pip install Pillow
            if errorlevel 1 (
                echo ERROR: Failed to install Pillow
                set INSTALL_FAILED=1
            ) else (
                echo Pillow installed successfully
            )
        )
        
        python -c "import numpy" >nul 2>&1
        if errorlevel 1 (
            echo Installing NumPy...
            python -m pip install numpy
            if errorlevel 1 (
                echo ERROR: Failed to install NumPy
                set INSTALL_FAILED=1
            ) else (
                echo NumPy installed successfully
            )
        )
        
        echo.
        if defined INSTALL_FAILED (
            echo.
            echo WARNING: Some packages failed to install.
            echo.
            echo.
            echo You can try installing manually with:
            echo ^> pip install Pillow numpy
            echo.
            pause
            exit /b 1
        ) else (
            echo --------------------------------------------------------
            echo All packages installed successfully!
            echo --------------------------------------------------------
            echo.
        )
    ) else (
        echo.
        echo Installation cancelled.
        echo.
        echo Please install required packages manually:
        echo   pip install Pillow numpy
        echo.
        pause
        exit /b 1
    )
)

cls
echo ============================================================
echo                    SELECT TOOL TO RUN
echo ============================================================
echo.
echo [1] Decal Modding Tool
echo [2] Packer Tool
echo [0] Exit
echo.
echo ============================================================
echo.

set /p TOOL_CHOICE="Enter your choice (1, 2, or 0): "

if "!TOOL_CHOICE!"=="1" (
    set SCRIPT_TO_RUN=main.py
    set TOOL_NAME=Decal Modding Tool
) else if "!TOOL_CHOICE!"=="2" (
    set SCRIPT_TO_RUN=packer.py
    set TOOL_NAME=Packer Tool
) else if "!TOOL_CHOICE!"=="0" (
    echo.
    echo Exiting...
    timeout /t 1 >nul
    exit /b 0
) else (
    echo.
    echo Invalid choice. Please run the launcher again and select 1, 2, or 0.
    echo.
    pause
    exit /b 1
)

if not exist "!SCRIPT_TO_RUN!" (
    echo.
    echo ============================================================
    echo ERROR: !SCRIPT_TO_RUN! not found in current directory!
    echo ============================================================
    echo.
    echo Please make sure you're running this batch file from
    echo the same folder as !SCRIPT_TO_RUN!
    echo.
    pause
    exit /b 1
)

echo.
echo.
echo Starting !TOOL_NAME!...
cls

python !SCRIPT_TO_RUN!

if errorlevel 1 (
    echo.
    echo.
    echo Program exited with an error.
    echo.
    echo.
)

pause