import logging
import time
from functools import wraps
from typing import Any, Callable


def backoff(
    exceptions: tuple[Any],
    start_sleep_time: float=0.1,
    factor: int=2,
    border_sleep_time: int=10,
):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ** n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
    :param border_sleep_time: максимальное время ожидания
    :return: результат выполнения функции
    """  # noqa: E501
    def func_wrapper(func: Callable):
        @wraps(func)
        def inner(*args: Any, **kwargs: Any):
            tries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logging.exception("Execution problem found.")
                sleep_time = start_sleep_time * (factor ** tries)
                time.sleep(
                    sleep_time
                    if sleep_time < border_sleep_time
                    else border_sleep_time,
                )
                tries += 1

        return inner
    return func_wrapper
