FROM python:3.7-slim
ARG env=production
ENV ENV=$env \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=0.12.11
RUN pip install "poetry==$POETRY_VERSION"
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN echo ${ENV}
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libc-dev \
  && rm -rf /var/lib/apt/lists/* \
  && poetry config settings.virtualenvs.create false \
  && poetry install $(test "$ENV" = "production" && echo "--no-dev") --no-interaction --no-ansi \
  && apt-get purge -y --auto-remove gcc libc-dev

COPY . /code
EXPOSE 5000
RUN chmod 644 ./entrypoint.py
RUN chmod 644 ./debug.py
CMD gunicorn --bind 0.0.0.0:5000 --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --access-logfile - --capture-output entrypoint:app 
