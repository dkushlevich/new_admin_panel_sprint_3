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
        "dbname": settings.postgres_db,
        "user": settings.postgres_user,
        "password": settings.postgres_password,
        "host": settings.postgres_host,
        "port": settings.postgres_port,
    }
    es_host = f"http://{settings.elastic_host}:{settings.elastic_port}"

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
            settings.table_names,
            settings.batch_size,
            settings.elastic_index,
        )(settings.loop_sleep_time)
