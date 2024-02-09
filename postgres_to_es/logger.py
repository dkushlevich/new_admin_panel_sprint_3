import logging
import sys
from pathlib import Path

logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s, %(levelname)s, %(message)s, "
            "%(lineno)s"
        ),
        stream=sys.stdout,
    )
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(
    Path(__file__).resolve().parent / "postgres_to_es.log",
)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
)
file_handler.setFormatter(formatter)

logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
