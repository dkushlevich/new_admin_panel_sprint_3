from psycopg2.extensions import connection as _connection


class BaseExtractor:
    """
    Базовый класс для извлечения данных из базы PostgreSQL.
    """

    def __init__(
        self,
        connection: _connection,
        query: str,
    ):
        self.connection = connection
        self.query = query

    def extract(self, **query_params):  # noqa: ANN003
        """
        Извлекает данные из базы данных с использованием
        предоставленного SQL-запроса.

        :kwargs **query_params: параметры, используемые для форматирования
        SQL-запроса.
        :return: результаты запроса.
        """
        query = self.query.format(**query_params)

        with self.connection.cursor() as curs:
            curs.execute(query=query)
            return curs.fetchall()
