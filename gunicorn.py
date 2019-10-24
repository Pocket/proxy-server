from multiprocessing import cpu_count
import os


def max_workers():
    return cpu_count()


bind = '0.0.0.0:8000'
timeout = os.environ.get('GUNICORN_TIMEOUT', 30)
worker_class = 'gevent'
worker_connections = os.environ.get('GUNICORN_CONNECTIONS', 1000)
workers = max_workers()
