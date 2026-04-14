#!/bin/bash

# Student Portal Setup Script

echo "=========================================="
echo "Student Portal - Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make migrations
echo ""
echo "Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo ""
echo "=========================================="
echo "Create Admin Account"
echo "=========================================="
echo "Please create an admin account to access the admin panel."
python manage.py createsuperuser

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the development server:"
echo "1. Activate virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "2. Run the server:"
echo "   python manage.py runserver"
echo ""
echo "Then open your browser and go to:"
echo "http://127.0.0.1:8000/"
echo ""
echo "Admin panel:"
echo "http://127.0.0.1:8000/admin/"
echo "=========================================="
