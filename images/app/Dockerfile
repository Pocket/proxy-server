FROM python:3.11.6-slim

ARG UID=${UID:-10001}
ARG GID=${GID:-10001}

ENV PIPENV_VENV_IN_PROJECT=1

RUN python -m pip install pipenv

RUN groupadd -g $GID app; \
  useradd -g $GID -u $UID -m -s /bin/bash app; \
  mkdir /app; \
  chown app:app /app

WORKDIR /app

COPY --chown=app:app . .

USER app

RUN pipenv install

ENV PATH=/app/.venv/bin:${PATH}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
