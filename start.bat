@echo off
echo Starting MOU Management System...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if database exists, if not create it
if not exist db.sqlite3 (
    echo Creating database...
    python manage.py migrate
    echo.
    echo Creating sample data...
    python manage.py create_sample_data
    echo.
)

echo Starting Django development server...
echo.
echo Access the application at: http://127.0.0.1:8000
echo Admin login: admin / admin123
echo.
python manage.py runserver

pause
