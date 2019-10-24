FROM python:3.7-stretch

COPY ./ /app/
WORKDIR /app
RUN pip install -r pip.lock

# Flask uses the create_app factory so Gunicorn should refer to this method specifically
ENTRYPOINT ["gunicorn", "-c", "gunicorn.py", "--log-level", "info", "app.main:create_app()"]
