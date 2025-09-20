"""
This module will change name to util.py in the next minor pre-release version
"""

from time import time


class Counter:
    _count: int = 0

    @staticmethod
    def increment(number: int = 1):
        Counter._count += number

    @staticmethod
    def reset():
        Counter._count = 0

    @staticmethod
    def get_count() -> int:
        return Counter._count


class Checkpoint:
    check_time: float
    description: str | None

    def __init__(self, check_time: float, description: str | None = None):
        self.check_time = check_time
        self.description = description

    def __str__(self):
        if self.description:
            return f"Checkpoint({self.check_time}, '{self.description}')"
        return f"Checkpoint({self.check_time})"


class Timer:
    """
    Timer class
    """

    start_timestamp: float
    end: float | None = None
    checkpoints: list[Checkpoint] = []

    def __init__(self):
        self.start_timestamp = time()
        self.checkpoints = []

    def stop(self):
        if self.end is not None:
            raise CallStopAfterStopException()
        self.end = time() - self.start_timestamp

    def add_checkpoint(self, description: str | None = None):
        self.checkpoints.append(Checkpoint(time() - self.start_timestamp, description))

    def __str__(self):
        return f"Timer({self.start_timestamp}, {self.end}, {self.checkpoints})"


# Exceptions
class CallStopAfterStopException(Exception):
    pass
