@echo off
REM Script to restart the backend server with the correct configuration

echo Stopping any existing backend processes...
taskkill /f /im uvicorn.exe 2>nul
if errorlevel 1 (
    echo No existing uvicorn processes found
)

echo Starting the backend server...
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

echo Backend server started successfully!
echo You can now access your API at http://localhost:8000