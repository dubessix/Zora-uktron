@echo off
setlocal
chcp 65001 >nul
title Ultron Personal V1
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ultron is not installed yet. Opening setup...
    call "SETUP_ULTRON_WINDOWS.bat"
    exit /b %errorlevel%
)

".venv\Scripts\python.exe" -m backend.app.cli start
if errorlevel 1 (
    echo.
    echo Ultron stopped with an error. Open Ultron Doctor or run setup repair.
    pause
    exit /b 1
)
endlocal
