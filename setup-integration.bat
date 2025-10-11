@echo off
REM Setup script for NMTSA LMS Integration (Windows)

echo ==========================================
echo NMTSA LMS - Frontend-Backend Integration
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)
if not exist "frontend" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

echo Step 1: Installing backend dependencies...
cd backend\nmtsa_lms

REM Check for uv first, then pip
where uv >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Using uv to install dependencies...
    uv sync
) else (
    echo Using pip to install dependencies...
    pip install -e .
)

echo.
echo Step 2: Creating database migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Step 3: Creating admin user...
python manage.py shell < ..\..\create_admin.py

echo.
echo Step 4: Installing frontend dependencies...
cd ..\..\frontend

REM Check for pnpm first, then npm
where pnpm >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Using pnpm to install dependencies...
    pnpm install
) else (
    where npm >nul 2>nul
    if %ERRORLEVEL% == 0 (
        echo Using npm to install dependencies...
        npm install
    ) else (
        echo Error: Neither npm nor pnpm found. Please install Node.js
        exit /b 1
    )
)

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo To start the development servers:
echo.
echo Terminal 1 (Backend):
echo   cd backend\nmtsa_lms
echo   python manage.py runserver
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo Then visit:
echo   Frontend: http://localhost:5173
echo   Admin Login: http://localhost:5173/admin-login
echo   API: http://localhost:8000/api/
echo.
echo Admin credentials:
echo   Username: admin
echo   Password: admin123
echo ==========================================

cd ..
pause
