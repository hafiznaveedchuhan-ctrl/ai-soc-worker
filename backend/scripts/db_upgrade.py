"""`make db-upgrade CONFIRM=haan` — apply Alembic migrations to SOC_DB_URL from backend/.env.

Writes to Neon → needs Naveed's explicit "haan". The URL is read from .env and never printed.
"""

import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from dotenv import dotenv_values

BACKEND = Path(__file__).resolve().parents[1]
GW = BACKEND / "services/api-gateway"

if os.environ.get("CONFIRM") != "haan":
    sys.exit("refused: migrating the Neon database needs CONFIRM=haan")
url = os.environ.get("SOC_DB_URL") or dotenv_values(BACKEND / ".env").get("SOC_DB_URL")
if not url:
    sys.exit("SOC_DB_URL is not set in backend/.env")
os.environ["SOC_DB_URL"] = url
cfg = Config(str(GW / "alembic.ini"))
cfg.set_main_option("script_location", str(GW / "migrations"))
command.upgrade(cfg, "head")
print("migrated to head (database name and host not printed)")
