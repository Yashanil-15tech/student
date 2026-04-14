@echo off
echo ==========================================
echo Student Portal - Setup Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Make migrations
echo.
echo Setting up database...
python manage.py makemigrations
python manage.py migrate

REM Create superuser
echo.
echo ==========================================
echo Create Admin Account
echo ==========================================
echo Please create an admin account to access the admin panel.
python manage.py createsuperuser

REM Collect static files
echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the development server:
echo 1. Activate virtual environment:
echo    venv\Scripts\activate
echo 2. Run the server:
echo    python manage.py runserver
echo.
echo Then open your browser and go to:
echo http://127.0.0.1:8000/
echo.
echo Admin panel:
echo http://127.0.0.1:8000/admin/
echo ==========================================
pause
