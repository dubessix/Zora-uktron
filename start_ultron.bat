@echo off
REM =============================================================================
REM  ULTRON — One-Command Launcher (Windows)
REM  Green, cool terminal vibe. Boots backend + frontend together.
REM =============================================================================
setlocal enabledelayedexpansion

chcp 65001 >nul
title ULTRON — Personal AI Operating System

REM ---- Colors (green cool vibe) ---------------------------------------------
set "GREEN=[92m"
set "DIM=[2;37m"
set "CYAN=[96m"
set "RED=[91m"
set "YELLOW=[93m"
set "RESET=[0m"
set "BOLD=[1m"

echo.
echo %GREEN%%BOLD%  ULTRON — Personal AI Operating System %RESET%
echo %DIM%  One-Command Launcher (Windows) %RESET%
echo %GREEN%  --------------------------------------------- %RESET%
echo.

cd /d "%~dp0"

REM ---- 0. .env check --------------------------------------------------------
if not exist ".env" (
    echo %YELLOW%[!] .env not found. Creating template...%RESET%
    copy ".env.example" ".env" >nul 2>&1
    if errorlevel 1 (
        echo %RED%[X] No .env.example either. Run 'ultron setup' or create .env manually.%RESET%
        pause
        exit /b 1
    )
    echo %YELLOW%[!] Edit .env and add your API keys, then run again.%RESET%
    echo %YELLOW%[!] Placeholder keys work too — Ultron runs in mock mode.%RESET%
)

REM ---- 1. Port check (rough, best-effort) ------------------------------------
echo %CYAN%[>] Checking ports...%RESET%
netstat -ano | findstr ":8000 " >nul 2>&1 && (
    echo %RED%[X] Port 8000 in use. Close it and retry.%RESET%
    pause
    exit /b 1
)
netstat -ano | findstr ":5173 " >nul 2>&1 && (
    echo %RED%[X] Port 5173 in use. Close it and retry.%RESET%
    pause
    exit /b 1
)
echo %GREEN%[✓] Ports 8000 & 5173 are free%RESET%

REM ---- 2. Frontend deps ------------------------------------------------------
if not exist "frontend\node_modules" (
    echo %CYAN%[>] Installing frontend dependencies (first run)...%RESET%
    pushd frontend
    call npm install
    popd
)

REM ---- 3. Boot backend -------------------------------------------------------
echo %CYAN%[>] Booting Ultron backend...%RESET%
start "ULTRON-Backend" /min cmd /c "cd /d %~dp0 && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

REM ---- 4. Boot frontend ------------------------------------------------------
echo %CYAN%[>] Booting Ultron frontend...%RESET%
start "ULTRON-Frontend" /min cmd /c "cd /d %~dp0\frontend && npm run dev -- --host 127.0.0.1"

REM ---- 5. Open browser --------------------------------------------------------
echo %CYAN%[>] Opening Ultron dashboard...%RESET%
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5173"

echo.
echo %GREEN%%BOLD%  Ultron is ONLINE. Systems synchronized. Awaiting your command, Sir.%RESET%
echo %DIM%  Close the two mini backend/frontend windows to stop, or run 'taskkill /f /im python.exe'.%RESET%
echo.
pause
