from .command import CommandResult


class RunnerRuntimeError(RuntimeError):

    def __init__(self, result: CommandResult, retry: int):
        self.result = result
        self.retry = retry

    def __str__(self):
        return f"RunnerRuntimeException({self.result.__str__()}, {self.retry})"

    def __repr__(self):
        return f"RunnerRuntimeException({self.result.__repr__()}, {self.retry})"

