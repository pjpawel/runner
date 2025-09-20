from time import time, sleep
from random import randint

import pytest

from src.runner_pjpawel import Counter
from src.runner_pjpawel.counter import Timer, CallStopAfterStopException


def test_counter_increment():
    last_counter = Counter.get_count()

    Counter.increment()

    assert last_counter + 1 == Counter.get_count()


def test_counter_reset():
    last_counter = Counter.get_count()
    Counter.increment()
    assert Counter.get_count() == 1 + last_counter

    Counter.reset()

    assert Counter.get_count() == 0


def test_timer_end():
    timestamp = time()
    timer = Timer()

    sleep(1.0 / randint(50, 100))

    timer.stop()
    timestamp_end = time()

    diff = timestamp_end - timestamp
    assert diff > timer.end
    assert diff < timer.end + 0.01


def test_timer_checkpoint():
    timestamp = time()
    timer = Timer()

    sleep(1.0 / randint(50, 100))

    timer.add_checkpoint()
    timestamp_check = time()

    assert len(timer.checkpoints) == 1
    check_time = timer.checkpoints[0].check_time
    diff_check = timestamp_check - timestamp
    assert diff_check > check_time
    assert diff_check < check_time + 0.01

    timer.stop()
    timestamp_end = time()

    diff = timestamp_end - timestamp
    assert diff > timer.end
    assert diff < timer.end + 0.01


def test_stop_called_2_times():
    with pytest.raises(CallStopAfterStopException):
        timer = Timer()
        timer.stop()
        assert timer.end is not None
        timer.stop()
