from pathlib import Path
from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

from secrets_management.manage import (  # NOQA
    decrypt_credentials,
    load_credentials,
)

load_credentials(decrypt_credentials(which=["*.env"]))


import asyncpg  # NOQA
from datetime import timedelta  # NOQA
from datetime import datetime  # NOQA
from utils.timescaledb.tsdb_manage import init_db, init_connection, get_pool  # NOQA

print(
    """=== Timescale REPL Loaded ===
To load TimescaleDB connection:
pool = await get_pool()
conn = await pool.acquire()
await conn.fetch(query, *params)
"""
)
