docker-compose run --rm tasks bash -c "PYTHONPATH=. alembic revision -m '$@' --autogenerate"