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

# Starting Gunicorn server...
echo "Starting Gunicorn server..."
cd /home/site/wwwroot
gunicorn -c gunicorn.conf.py app.main:app