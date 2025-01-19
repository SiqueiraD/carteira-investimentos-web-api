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
chdir = os.path.dirname(os.path.abspath(__file__))
pythonpath = os.path.dirname(os.path.abspath(__file__))

# Reload
reload = True
reload_extra_files = [
    os.path.join(chdir, "app", "main.py"),
    os.path.join(chdir, "app", "config.py")
]

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
    print(f"Worker directory: {os.getcwd()}")
    print(f"Worker PYTHONPATH: {os.environ.get('PYTHONPATH', '')}")
    print(f"Worker sys.path: {sys.path}")
    try:
        import app.main
        print("Successfully imported app.main")
    except Exception as e:
        print(f"Failed to import app.main: {e}")
        print(f"sys.path: {sys.path}")

def worker_abort(worker):
    print(f"Worker {worker.pid} aborted")
    print(f"Last error: {getattr(worker, 'last_error', None)}")

# WSGI app
wsgi_app = "app.main:app"
