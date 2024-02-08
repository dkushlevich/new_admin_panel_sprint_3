import abc
import json
from datetime import datetime
from typing import Any, Dict

from redis import Redis


class BaseStorage(abc.ABC):
    """Абстрактное хранилище состояния.

    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""


class DateTimeEncoder(json.JSONEncoder):

    def default(self, obj: Any):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class RedisStorage(BaseStorage):
    """Реализация хранилища, использующего Redis.
    """

    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        json_string = json.dumps(state, cls=DateTimeEncoder)
        self.redis_adapter.set("etl_data", json_string)

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        json_string = self.redis_adapter.get("etl_data")
        return json.loads(json_string) if json_string else {}

    def _serialize_datetime(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
