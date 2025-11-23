import multiprocessing
import os

# Gunicorn configuration file

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Workers configuration
# For CPU bound apps: 2 * CPUs + 1
# For I/O bound apps (like this one with DB and API calls): 2-4 * CPUs
workers_per_core = 2
cores = multiprocessing.cpu_count()
default_web_concurrency = workers_per_core * cores
web_concurrency = os.getenv("WEB_CONCURRENCY", None)
workers = int(web_concurrency) if web_concurrency else default_web_concurrency

# Worker class
# Uvicorn worker for FastAPI (ASGI)
worker_class = "uvicorn.workers.UvicornWorker"

# Threads per worker (Gunicorn default is 1)
threads = 1

# Timeout
# Increase timeout for long running tasks if necessary, though we use background tasks now.
timeout = 120

# Keepalive
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
