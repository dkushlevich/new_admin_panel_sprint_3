import logging
from datetime import datetime
from typing import Any

from psycopg2.extensions import connection as _connection
from redis import Redis

from extract.base import BaseExtractor
from extract.sql_queries import (
    FILMWORK_BY_IDS_SQL,
    FILMWORK_IDS_BY_RELATED_MODIFIED_SQL,
    MODIFIED_OBJECTS_SQL,
)
from settings import settings
from state.base import State
from state.storage import RedisStorage


class PostgreSQLExtractor:
    """
    Класс для извлечения и обогащения данных из PostgreSQL.
    """

    def __init__(
        self,
        connection: _connection,
        batch_size: int,
        table_names: list[str],
    ):
        self.connection = connection
        self.batch_size = batch_size

        redis = Redis(
            host=settings.REDIS_HOST,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        storage = RedisStorage(redis)
        self.state = State(storage)
        self._check_states(table_names)

        self.producer = BaseExtractor(
            self.connection,
            MODIFIED_OBJECTS_SQL,
        )
        self.enricher = BaseExtractor(
            self.connection,
            FILMWORK_IDS_BY_RELATED_MODIFIED_SQL,
        )
        self.merger = BaseExtractor(
            self.connection,
            FILMWORK_BY_IDS_SQL,
        )

    def extract_data(self, table_name: str) -> list[list[str]]:
        """
        Запускает процесс извлечения и обогащения данных для
        определённой таблицы.

        :param table_name: название таблицы
        :return: список фильмов, которых затронуло изменение записи таблицы
        """
        modified_ids = self._produce_data(table_name)
        filmworks_ids = self._enrich_data(
            table_name,
            modified_ids,
        )
        return self._merge_data(filmworks_ids)

    def _check_states(self, table_names: list[str]) -> None:
        """
        Проверяет стейты таблиц в хранилище, если стейт не обнаружен -
        инициализирует его с минимальным значением.
        """
        for table_name in table_names:
            if not self.state.get_state(f"{table_name}_modified"):
                self.state.set_state(f"{table_name}_modified", datetime.min)

    def _produce_data(self, table_name: str) -> str:
        """
        Забирает модифицированные записи таблицы из хранилища
        и обновляет стейт.

        :param table_name: название таблицы
        :return: строка с id изменённых записей в виде '(id1, id2)'
        """
        modified_data = self.producer.extract(
            table_name=table_name,
            modified=self.state.get_state(
                f"{table_name}_modified",
            ),
            batch_size=self.batch_size,
        )
        if not modified_data:
            raise EOFError

        self.last_modified = modified_data[-1]["modified"]


        self.state.set_state(
            f"{table_name}_modified", self.last_modified,
        )
        modified_ids = [row["id"] for row in modified_data]

        logging.info(
            f"Found {len(modified_ids)} modified records "
            f"in {table_name} table",
        )

        return f"({str(modified_ids)[1:-1]})"

    def _enrich_data(
        self, table_name: str, modified_ids: str,
    ) -> str:
        """
        Забирает из базы список фильмов, которых затронуло изменение записей
        в таблице.

        :param table_name: название таблицы
        :param modified_ids: id изменённых записей таблице в виде '(id1, id2)'
        :return: id фильмов, которых затронуло изменение записей
        """
        if table_name == "film_work":
            return modified_ids

        filmwork_ids = self.enricher.extract(
            table_name=table_name,
            modified_ids=modified_ids,
        )
        modified_ids = [row["id"] for row in filmwork_ids]
        return f"({str(modified_ids)[1:-1]})"

    def _merge_data(
        self,
        filmworks_ids: str,
    ) -> list[dict[str, Any]]:
        """
        Обогащает raw id данные.

        :param filmworks_ids: id изменённых записей таблице в виде '(id1, id2)'
        :return: список фильмов с необходимой для трансформации информацией.
        """
        return self.merger.extract(
            filmworks_ids=filmworks_ids,
        )
