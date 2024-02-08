import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import DictCursor


@contextmanager
def open_postgres_db(dsn: dict):
    """Контекст-менеджер для соединения с базой данных PostgreSQL.

    :param dsn: Данные, необходимые для подключения.
    :yield: Объект connection(подключение к базе данных PostgreSQL)
    """
    conn = psycopg2.connect(**dsn, cursor_factory=DictCursor)
    try:
        logging.info("PostgreSQL creating connection")
        yield conn
    finally:
        logging.info("PostgreSQL closing connection")
        conn.commit()
        conn.close()
