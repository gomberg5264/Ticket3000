# Gunicorn configuration file
import multiprocessing
from main import initialize_app

# Binding
bind = "0.0.0.0:5000"

# Worker processes
workers = 2

# Threads per worker
threads = 2

# Worker class
worker_class = "sync"

# Timeout
timeout = 120

# Access log - records incoming HTTP requests
accesslog = "-"

# Error log - records Gunicorn server goings-on
errorlog = "-"

# Whether to send Flask output to the error log 
capture_output = True

# How verbose the Gunicorn error logs should be 
loglevel = "debug"

# Application module
wsgi_app = "main:app"

# Custom hook to run initialize_app() before starting workers
def on_starting(server):
    initialize_app()
