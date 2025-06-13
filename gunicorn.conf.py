"""
Gunicorn configuration for WolfPy production deployment.

This configuration provides optimized settings for running WolfPy applications
in production environments with proper logging, worker management, and security.
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')  # stdout
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')   # stderr
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'wolfpy'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if certificates are provided)
keyfile = os.getenv('SSL_KEYFILE')
certfile = os.getenv('SSL_CERTFILE')

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Application-specific settings
raw_env = [
    f'WOLFPY_ENV={os.getenv("WOLFPY_ENV", "production")}',
    f'DEBUG={os.getenv("DEBUG", "False")}',
]

# Worker timeout and graceful shutdown
graceful_timeout = 30
timeout = 30

# Enable stats if requested
if os.getenv('GUNICORN_STATS', '').lower() == 'true':
    statsd_host = os.getenv('STATSD_HOST', 'localhost:8125')

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("WolfPy server is ready. Listening on %s", server.address)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

# Development vs Production settings
if os.getenv('WOLFPY_ENV') == 'development':
    # Development settings
    workers = 1
    reload = True
    reload_extra_files = ['templates/', 'static/']
    loglevel = 'debug'
    timeout = 120
else:
    # Production settings
    preload_app = True
    worker_class = 'gevent'  # Use gevent for better concurrency
    worker_connections = 1000
