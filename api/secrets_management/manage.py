import os
from io import StringIO
from dotenv import load_dotenv
from pathlib import Path
from cryptography.fernet import Fernet


ENCRYPTED_PATH = './.encrypted/production.env'
PLAINTEXT_PATH = './production.env'


def get_environment() -> str:
    return os.environ.get('ENV', 'development')


def load_credentials(credentials: str) -> None:
    filelike = StringIO(credentials)
    filelike.seek(0)
    load_dotenv(stream=filelike)


def decrypt_credentials():
    env = get_environment()
    secret_key = os.environ.get(f'APP_SECRET_{env.upper()}', None)
    if secret_key is None or secret_key == '':
        print('[MANAGE] No secrets will be loaded')
        return None
    f = Fernet(secret_key)
    try:
        fp = open(ENCRYPTED_PATH, 'rb')
        secret = fp.read()
        fp.close()
        credentials = f.decrypt(secret)
        print('[MANAGE] Decrypted successfully')
        return credentials.decode("utf-8")
    except:
        print('[MANAGE] Decryption key was loaded but secrets were not found.')
        print('[MANAGE] No secrets will be loaded')
        return None


def rotate_credentials():
    secret_key = Fernet.generate_key()
    replace_credentials(secret_key)
    fp = open('./.secrets/key', 'wb')
    fp.write(secret_key)
    fp.close()
    print("[MANAGE] Secret key replaced in .secrets/key")


def encrypt_credentials():
    env = get_environment()
    secret_key = os.environ.get(f'APP_SECRET_{env.upper()}', None)
    if secret_key is None:
        raise Exception(f'{env}: No key present, check environment variables')
    return replace_credentials(secret_key)


def replace_credentials(secret_key):
    f = Fernet(secret_key)
    fp = open(PLAINTEXT_PATH, 'rb')
    secret = fp.read()
    fp.close()
    encrypted = f.encrypt(secret)
    fp = open(ENCRYPTED_PATH, 'wb')
    fp.write(encrypted)
    fp.close()
    print('[MANAGE] Encrypted secrets')
