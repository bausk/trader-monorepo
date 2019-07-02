FROM python:3.7-slim
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=0.12.11
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN  poetry config settings.virtualenvs.create false \
  && poetry install $(test "$FLASK_ENV"=production && echo "--no-dev") --no-interaction --no-ansi

COPY . /code
RUN chmod 644 ./api.py
ENTRYPOINT poetry run python ./api.py
