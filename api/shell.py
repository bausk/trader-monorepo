import os
from aiohttp import web
from dotenv import load_dotenv
from pathlib import Path
import click
from secrets_management.manage import encrypt_credentials, decrypt_credentials, load_credentials

print('Loading development env...')
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


@click.command()
@click.option('--env', help='Environment to encrypt the secrets for.')
def cli(env):
    print(f'Encrypting env: {env}...')
    encrypt_credentials(env)
    print(f'Test loading env: {env}...')
    load_credentials(decrypt_credentials(env))
    print('Done.')


if __name__ == '__main__':
    cli()
