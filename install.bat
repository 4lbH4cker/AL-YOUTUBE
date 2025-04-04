@echo off
:: AL-YOUTUBE Downloader - Auto Installer
:: =====================================
:: This script will install everything needed automatically
:: Works on Windows 10/11 64-bit systems

setlocal enabledelayedexpansion

:: Admin Check
net session >nul 2>&1
if %errorlevel% == 0 (
    set ADMIN_MODE=1
) else (
    set ADMIN_MODE=0
)

:: Colors
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
    set "DEL=%%a"
)
set "RED=%DEL%"
set "GREEN=%DEL%"
set "YELLOW=%DEL%"
set "RESET=%DEL%"

:: Title
title AL-YOUTUBE Downloader - Instalim Automatik

:: Main Install Function
:MAIN
cls
echo.
echo %GREEN%===============================================
echo %GREEN%  AL-YOUTUBE DOWNLOADER - INSTALIM AUTOMATIK  %RESET%
echo %GREEN%===============================================
echo.

:: 1. Check Python
echo %YELLOW%[1/4] Kontrolloj nese Python eshte i instaluar...%RESET%
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%Python nuk eshte i instaluar. Po e instaloj automatikisht...%RESET%
    call :INSTALL_PYTHON
    if %ERRORLEVEL% neq 0 (
        echo %RED%Deshtoi instalimi i Python. Ju lutem instalojeni manualisht.%RESET%
        pause
        exit /b 1
    )
    :: Refresh PATH
    call :REFRESH_PATH
) else (
    python --version
    echo %GREEN%Python eshte i instaluar!%RESET%
)

:: 2. Install yt-dlp
echo.
echo %YELLOW%[2/4] Po instaloje yt-dlp...%RESET%
pip install --upgrade yt-dlp >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%Deshtoi instalimi standard, provoj me --user...%RESET%
    pip install --user --upgrade yt-dlp >nul 2>&1
    if %errorlevel% neq 0 (
        echo %RED%Deshtoi instalimi i yt-dlp%RESET%
        pause
        exit /b 1
    )
)
echo %GREEN%yt-dlp u instalua me sukses!%RESET%

:: 3. Install Tkinter
echo.
echo %YELLOW%[3/4] Po instaloje Tkinter...%RESET%
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    pip install tk >nul 2>&1
    if %errorlevel% neq 0 (
        echo %RED%Deshtoi instalimi i Tkinter%RESET%
        pause
        exit /b 1
    )
)
echo %GREEN%Tkinter u instalua me sukses!%RESET%

:: 4. Download the main script
echo.
echo %YELLOW%[4/4] Po shkarkoj programin kryesor...%RESET%
if not exist "al_youtube.py" (
    curl -L -o al_youtube.py "https://raw.githubusercontent.com/example/al_youtube/main/al_youtube.py" >nul 2>&1
    if %errorlevel% neq 0 (
        echo %RED%Deshtoi shkarkimi i programit kryesor%RESET%
        pause
        exit /b 1
    )
)
echo %GREEN%Programi u shkarkua me sukses!%RESET%

:: Final
echo.
echo %GREEN%===============================================
echo %GREEN%  INSTALIMI U KRYE ME SUKSES!  %RESET%
echo %GREEN%===============================================
echo.
echo Tani mund ta ekzekutoni programin me komanden:
echo.
echo    python al_youtube.py
echo.
echo Ose thjesht klikoni dy here ne skedarin al_youtube.py
echo.
pause
exit /b 0

:: Functions
:INSTALL_PYTHON
echo %YELLOW%Po shkarkoj Python...%RESET%
curl -L -o python_installer.exe "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe" >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%Deshtoi shkarkimi i Python%RESET%
    exit /b 1
)

echo %YELLOW%Po instaloje Python...%RESET%
start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
if %errorlevel% neq 0 (
    echo %RED%Deshtoi instalimi i Python%RESET%
    exit /b 1
)

del python_installer.exe >nul 2>&1
exit /b 0

:REFRESH_PATH
echo %YELLOW%Po rifreskoj variablat e sistemit...%RESET%
setx PATH "%PATH%" >nul
exit /b 0