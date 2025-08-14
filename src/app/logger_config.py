import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "application.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)
logger.info(f"We use the next encoding - {sys.stdout.encoding}")
