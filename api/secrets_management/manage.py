import os
from io import StringIO
from dotenv import load_dotenv
from pathlib import Path
from cryptography.fernet import Fernet
import hashlib


ENCRYPTED_PATH = './.encrypted'
PLAINTEXT_SECRETS = {
    'production': [
        './production.env',
        ],
    'staging': [
        './staging.env',
        ],    
    }


def get_name_digest(filename):
    m = hashlib.shake_256()
    m.update(filename.encode())
    return m.hexdigest(32), m.hexdigest(4)


def get_environment() -> str:
    return os.environ.get('ENV', 'development')


def load_credentials(credentials) -> None:
    if credentials:
        for credential_string in credentials:
            filelike = StringIO(credential_string)
            filelike.seek(0)
            load_dotenv(stream=filelike)


def decrypt_credentials(env=None):
    if env is None:
        env = get_environment()
    secret_key = os.environ.get(f'APP_SECRET_{env.upper()}', None)
    integrity_checks = (
        secret_key is None,
        secret_key == '',
        env is None,
        env == '',
    )
    if any(integrity_checks):
        print('[Pysecrets] No secrets will be loaded')
        return None
    f = Fernet(secret_key)
    
    decrypted = []
    files_to_decrypt = PLAINTEXT_SECRETS.get(env)
    if files_to_decrypt is None:
        return decrypted
    
    for file_to_decrypt in files_to_decrypt:
        filekey, digest = get_name_digest(file_to_decrypt)
        path = Path(ENCRYPTED_PATH, filekey)
        try:
            fp = open(path, 'rb')
            secret = fp.read()
            fp.close()
            credential = f.decrypt(secret).decode("utf-8")
            decrypted.append(credential)
            print(f'   ...Decrypted successfully. Digest: {digest}')
        except:
            print(f'   Secret not found. Digest: {digest}')
            print('   No secret was loaded')
    return decrypted


def rotate_credentials(env):
    if env is None or env == '':
        raise RuntimeError('Environment was not explicitly specified during credentials rotation')
    secret_key = Fernet.generate_key()
    replace_credentials(secret_key, env)
    fp = open('./.secrets/key', 'wb')
    fp.write(secret_key)
    fp.close()
    print("   Secret key replaced in .secrets/key")


def encrypt_credentials(env: str):
    if env is None or env == '':
        raise RuntimeError('Environment was not explicitly specified during encryption')
    secret_key = os.environ.get(f'APP_SECRET_{env.upper()}', None)
    if secret_key is None:
        raise Exception(f'{env}: No APP_SECRET_{env.upper()} variable found for specified environment')
    return replace_credentials(secret_key, env)


def replace_credentials(secret_key: str, env: str):
    integrity_checks = (
        secret_key is None,
        secret_key == '',
        env is None,
        env == '',
    )
    if any(integrity_checks):
        raise RuntimeError('Bad parameter received when replacing credentials')
    f = Fernet(secret_key)
    path = Path(ENCRYPTED_PATH)
    # for child in path.glob('*'):
    #     if child.is_file():
    #         child.unlink()
    files_to_encrypt = PLAINTEXT_SECRETS.get(env)
    for x, file_to_encrypt in enumerate(files_to_encrypt):
        filekey, digest = get_name_digest(file_to_encrypt)
        path_from = Path(file_to_encrypt)
        path_to = Path(ENCRYPTED_PATH, filekey)
        fp = open(path_from, 'rb')
        secret = fp.read()
        fp.close()
        encrypted = f.encrypt(secret)
        fp = open(path_to, 'wb')
        fp.write(encrypted)
        fp.close()
        print(f'   ...Encrypted secret. Digest: {digest}')
