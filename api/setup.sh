git submodule update --init --recursive
pip install poetry
poetry config virtualenvs.in-project true
poetry install
docker-compose build