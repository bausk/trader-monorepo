FROM python:3.7-slim
ARG POETRY_VERSION=0.12
ENV POETRY_VERSION=$POETRY_VERSION
COPY . /code
WORKDIR /code
RUN pip install 'poetry==$POETRY_VERSION'
RUN poetry install
ENTRYPOINT python ./mypackage/run.py
