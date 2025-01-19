import multiprocessing
import os
import sys

# Debug: Print current directory and Python path
print(f"Current directory: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', '')}")
print(f"sys.path: {sys.path}")

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 600
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "debug"
capture_output = True

# Process naming
proc_name = "investimentos_api"

# Working directory and Python path
chdir = "/home/site/wwwroot"
pythonpath = "/home/site/wwwroot"

# Reload
reload = False  # Desabilitado em produção
reload_extra_files = []

# Debug hooks
def on_starting(server):
    print("Starting Gunicorn server...")
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir()}")
    print(f"App directory contents: {os.listdir('app') if os.path.exists('app') else 'app dir not found'}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', '')}")
    print(f"sys.path: {sys.path}")

def post_worker_init(worker):
    print(f"Initializing worker {worker.pid}")
    try:
        from app.main import app
        print("Successfully imported app.main")
    except Exception as e:
        print(f"Error importing app.main: {e}")
        sys.exit(1)

def worker_abort(worker):
    print(f"Worker {worker.pid} aborted")
    print(f"Last error: {getattr(worker, 'last_error', None)}")

# WSGI app
wsgi_app = "app.main:app"
