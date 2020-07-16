from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

from secrets_management.manage import decrypt_credentials, load_credentials, get_environment
load_credentials(decrypt_credentials(which=['*.env']))

import asyncpg
from datetime import timedelta
from datetime import datetime
from utils.timeseries.timescale_utils import init_db, init_connection, get_pool

print("""=== Timescale REPL Loaded ===
To load TimescaleDB connection:
pool = await get_pool()
conn = await pool.acquire()
await conn.fetch(query, *params)
""")