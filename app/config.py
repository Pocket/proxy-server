from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # gunicorn
    gunicorn_bind: str = "0.0.0.0:8000"
    gunicorn_worker_class: str = "uvicorn.workers.UvicornWorker"
    gunicorn_workers: int = 4
