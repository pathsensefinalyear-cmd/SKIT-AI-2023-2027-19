@echo off
title PathSense AI - Full Stack Launcher
cls
echo =====================================================================
echo       PATHSENSE: REAL-TIME EDGE-VISION FOR ROAD CONDITION MAPPING    
echo       SKIT Jaipur - 7th Sem Minor Project (CS-AI)
echo =====================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [Setup] Virtual environment not found. Checking uv...
    where uv >nul 2>&1
    if %errorlevel% neq 0 (
        echo [Setup] Installing uv package manager...
        powershell -ExecutionPolicy RemoteSigned -Command "irm https://astral.sh/uv/install.ps1 | iex"
        set "Path=%USERPROFILE%\.local\bin;%Path%"
    )
    echo [Setup] Creating virtual environment (.venv)...
    uv venv .venv --python 3.12
    echo [Setup] Installing dependencies...
    uv pip install --python .venv\Scripts\python.exe -r requirements.txt
)

echo [Launch] Starting Full-Stack PathSense (Backend + Frontend + Database)...
.venv\Scripts\python.exe start_pathsense.py --mode all

pause
