#!/usr/bin/python
from secrets_management import rotate_credentials
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


rotate_credentials()
