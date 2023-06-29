import time
from typing import Callable

from src.auxiliary.logger import logger


class Stopwatch:
    def __init__(self, name: str = 'function', on_finish: Callable[[float], None] = None):
        self.start_time = None
        self.name = name
        self.on_finish = on_finish

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        delta = time.time() - self.start_time
        if self.on_finish:
            self.on_finish(delta)
        else:
            logger.info(f'Executed {self.name} in {delta} seconds.')
