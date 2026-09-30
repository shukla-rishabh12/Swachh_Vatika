"""
Gunicorn config for Render deployment.
"""
import os

bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"