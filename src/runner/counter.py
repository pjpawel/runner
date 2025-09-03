
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