from dotenv import load_dotenv
from pathlib import Path
import os


# Set home directory
project_dir = Path(__file__).parent
os.chdir(project_dir)


# Load development vars
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
