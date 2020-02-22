from cryptography.fernet import Fernet
import os


def get_environment() -> str:
    return os.environ.get('ENV', 'development')


def decrypt_credentials():
    env = get_environment()
    secret_key = os.environ.get(f'APP_SECRET_{env.upper()}', None)
    if secret_key is None:
        return b'{}'
    f = Fernet(secret_key)
    fp = open('./.encrypted/keyring.json', 'rb')
    secret = fp.read()
    fp.close()
    credentials = f.decrypt(secret)
    print('Decrypted')
    return credentials


def rotate_credentials():
    secret_key = Fernet.generate_key()
    replace_credentials(secret_key)
    fp = open('./.secrets/key', 'wb')
    fp.write(secret_key)
    fp.close()
    print("Secret key replaced in .secrets/key")


def encrypt_credentials():
    env = get_environment()
    secret_key = os.environ.get(f'APP_SECRET_{env.upper()}', None)
    if secret_key is None:
        raise Exception(f'{env}: No key present, check environment variables')
    return replace_credentials(secret_key)


def replace_credentials(secret_key):

    f = Fernet(secret_key)
    fp = open('./.secrets/keyring.json', 'rb')
    secret = fp.read()
    fp.close()
    encrypted = f.encrypt(secret)
    fp = open('./.encrypted/keyring.json', 'wb')
    fp.write(encrypted)
    fp.close()
    print('Encrypted')
