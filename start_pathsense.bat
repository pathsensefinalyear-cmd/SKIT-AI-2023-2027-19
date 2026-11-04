@echo off
title PathSense AI: One-Click System Launcher
color 0B

echo =======================================================================
echo          PATHSENSE AI: REAL-TIME ROAD CONDITION MAPPING
echo     SKIT Jaipur - 7th Semester B.Tech Minor Project (CS-AI)
echo =======================================================================
echo Team Members:
echo   1. Sharafat Khan  (23ESKCA098)
echo   2. Soham Manocha  (23ESKCA102)
echo   3. Sourabh Nagar  (23ESKCA105)
echo   4. Vedic Baurasi  (23ESKCA119)
echo =======================================================================
echo.

cd /d "%~dp0"

:: Detect Python executable
set PYTHON_CMD=python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "C:\Users\nagar\AppData\Local\Programs\Python\Python310\python.exe" (
        set PYTHON_CMD="C:\Users\nagar\AppData\Local\Programs\Python\Python310\python.exe"
    ) else (
        echo [ERROR] Python was not found in PATH or standard directory!
        pause
        exit /b 1
    )
)

echo [1/2] Launching PathSense Backend REST API on port 8000...
start "PathSense Backend REST API (Port 8000)" %PYTHON_CMD% backend/run_backend.py --port 8000

echo [INFO] Waiting 2 seconds for backend to bind to http://127.0.0.1:8000...
timeout /t 2 /nobreak >nul

echo [2/2] Launching PathSense Interactive Dashboard...
echo.
echo =======================================================================
echo   Dashboard UI : http://localhost:8501
echo   REST API     : http://127.0.0.1:8000
echo   Health Check : http://127.0.0.1:8000/api/v1/health
echo =======================================================================
echo.

%PYTHON_CMD% -m streamlit run dashboard/app.py --server.port 8501 --browser.gatherUsageStats false

pause
