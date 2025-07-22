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

echo Starting Celery worker for AI analysis...
start /B "Celery Worker" cmd /c "celery -A mou_management worker --loglevel=info --pool=solo"
echo Celery worker started in background.
echo.

echo Starting Django development server...
echo.
echo Access the application at: http://127.0.0.1:8000
echo Admin login: admin / admin123
echo.
echo Note: Celery worker is running in background for AI analysis.
echo Close this window to stop both services.
echo.
python manage.py runserver

pause
