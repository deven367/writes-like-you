import os
from pathlib import Path

from dotenv import load_dotenv


def load_config():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    token = os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID")
    if not token or not database_id:
        raise ValueError("Set NOTION_TOKEN and NOTION_DATABASE_ID in the environment or project-root .env.")
    return token, database_id
