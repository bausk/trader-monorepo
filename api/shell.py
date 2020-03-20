import os
from aiohttp import web
from dotenv import load_dotenv
from pathlib import Path

print('Loading development env...')
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

print('Encrypting production env...')
from secrets_management.manage import encrypt_credentials, decrypt_credentials, load_credentials
encrypt_credentials()

print('Test loading production env...')
load_credentials(decrypt_credentials())
print('Done.')