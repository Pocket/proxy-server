from app.config import Settings

settings = Settings()

bind = settings.gunicorn_bind
worker_class = settings.gunicorn_worker_class
workers = settings.gunicorn_workers
