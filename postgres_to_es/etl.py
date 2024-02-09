import time
from itertools import cycle

from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as _connection

from extract.extractor import PostgreSQLExtractor
from logger import logger
from transform.transformer import DataTransfromer
from upload.uploader import ESUploader


class ETL:

    def __init__(
        self,
        pg_connection: _connection,
        es_connection: Elasticsearch,
        table_names: list[str],
        batch_size: int,
        index: str,
    ) -> None:
        self.pg_extractor = PostgreSQLExtractor(
            pg_connection,
            batch_size,
            table_names,
        )
        self.data_transformer = DataTransfromer()
        self.es_uploader = ESUploader(es_connection)
        self.table_names = table_names
        self.index = index

        logger.info("ETL initialize completed.")

    def __call__(self, sleep_time: int):
        for table_name in cycle(self.table_names):
            logger.info(
                f"Looking for modified records in {table_name}",
            )
            try:
                data = self.pg_extractor.extract_data(table_name)
                logger.info(
                    f"Modified recods succesfully extracted "
                    f"from table {table_name}.",
                )
            except EOFError:
                logger.info("No modified data found.")
                continue

            transformed_data = self.data_transformer.transform(data)
            logger.info(
                f"Data for {table_name} ready for load to ES.",
            )

            self.es_uploader.insert_data(transformed_data, self.index)
            logger.info(
                "Records upload to ES.",
            )

            self.pg_extractor.update_state(table_name)
            logger.info(f"State for table {table_name} updated")

            time.sleep(sleep_time)
