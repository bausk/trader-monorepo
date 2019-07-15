#!/usr/bin/python
from aiohttp import web
from asyncio import Queue
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

from google.cloud import client