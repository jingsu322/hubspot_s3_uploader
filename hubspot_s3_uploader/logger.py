"""Project‑wide logging setup (console + rotating file)."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "job.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

root = logging.getLogger()
root.setLevel(logging.INFO)

# Console handler – good for container stdout
_cons = logging.StreamHandler()
_cons.setFormatter(_formatter)
root.addHandler(_cons)

# Rotating file – keep last 5×5 MB logs
_file = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=5)
_file.setFormatter(_formatter)
root.addHandler(_file)