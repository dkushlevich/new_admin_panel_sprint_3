from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

from utils.decorators import backoff


class ESUploader:
    """Класс для загрузки данных в индекс Elasticsearch"""

    def __init__(self, connection: Elasticsearch):
        self.es_connection = connection

    @backoff((ConnectionError,))
    def insert_data(self, data: list[dict], index:str) -> None:
        """
        Загружает данные в индекс movies
        :param data: Данные для загрузки в индекс
        """
        self.es_connection.bulk(
            index=index,
            body=data,
            refresh=True,
        )
