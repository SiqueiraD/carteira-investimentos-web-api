#!/bin/bash

# Adicionar o diretório atual ao PYTHONPATH
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Create and activate virtual environment
python -m venv antenv
source antenv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start the application
gunicorn main:app --bind=0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker --timeout 600