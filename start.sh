#!/bin/bash
echo "Starting MOU Management System..."
echo

# Activate virtual environment
source venv/bin/activate

# Check if database exists, if not create it
if [ ! -f db.sqlite3 ]; then
    echo "Creating database..."
    python manage.py migrate
    echo
    echo "Creating sample data..."
    python manage.py create_sample_data
    echo
fi

echo "Starting Django development server..."
echo
echo "Access the application at: http://127.0.0.1:8000"
echo "Admin login: admin / admin123"
echo
python manage.py runserver
