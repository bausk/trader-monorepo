echo 'Encrypting...'
docker-compose run --rm --entrypoint="bash -c 'python shell.py --env=staging && python shell.py --env=production'" api
