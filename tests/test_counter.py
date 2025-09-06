from src.runner_pjpawel import Counter


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