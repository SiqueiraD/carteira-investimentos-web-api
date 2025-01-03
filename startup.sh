#!/bin/bash

# Create and activate virtual environment
python -m venv antenv
source antenv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start the application
gunicorn app.main:app --bind=0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker --timeout 600