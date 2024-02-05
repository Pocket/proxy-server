FROM python:3.11.6 as base

ENV PIPENV_VENV_IN_PROJECT=1

RUN python -m pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy

FROM python:3.11.6-slim

ARG UID=${UID:-10001}
ARG GID=${GID:-10001}

RUN groupadd -g $GID app; \
  useradd -g $GID -u $UID -m -s /bin/bash app; \
  mkdir /app; \
  chown app:app /app

COPY --from=base /.venv /.venv

WORKDIR /app

COPY --chown=app:app . .

USER app

ENV PATH=/.venv/bin:${PATH}

CMD ["gunicorn", "--config", "gunicorn.py", "app.main:app"]
