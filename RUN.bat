@echo off
echo ========================================
echo  GreenCloud Storage - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Initialize database if not exists
if not exist "database\greencloud.db" (
    echo Initializing database...
    python init_db.py
    echo.
)

REM Run the application
echo Starting GreenCloud Server...
echo.
python app.py

pause
