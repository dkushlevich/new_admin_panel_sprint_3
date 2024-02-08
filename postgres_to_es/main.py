import logging
import sys
from pathlib import Path

from elasticsearch import Elasticsearch

from etl import ETL
from settings import settings
from utils.managers import open_postgres_db

if __name__ == "__main__":
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

    logger.info("Script running")

    DSN = {
        "dbname": settings.POSTGRES_DB,
        "user": settings.POSTGRES_USER,
        "password": settings.POSTGRES_PASSWORD,
        "host": settings.POSTGRES_HOST,
        "port": settings.POSTGRES_PORT,
    }
    es_host = f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"

    with (
        open_postgres_db(DSN) as pg_connection,
        Elasticsearch(es_host) as es_connection,
    ):
        logger.info(
            "PostgreSQL and ElasticSearch connect success",
        )
        ETL(
            pg_connection,
            es_connection,
            settings.TABLE_NAMES,
            settings.BATCH_SIZE,
        )(settings.LOOP_SLEEP_TIME)
