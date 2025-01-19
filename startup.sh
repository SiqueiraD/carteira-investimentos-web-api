#!/bin/bash

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH

# Debug: Show environment
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls)"
echo "App directory contents: $(ls app)"
echo "PYTHONPATH: $PYTHONPATH"
echo "sys.path: $(python -c "import sys; print(sys.path)")"

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Debug: Test imports
echo "Testing imports..."
python -c "import sys; print('Python path:', sys.path); from app.main import app; print('Successfully imported app.main')"

# Starting Gunicorn server...
echo "Starting Gunicorn server..."
gunicorn app.main:app --bind=0.0.0.0:8000 --timeout 600 --workers 4 --worker-class uvicorn.workers.UvicornWorker