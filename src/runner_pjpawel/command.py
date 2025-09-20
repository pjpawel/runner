import logging
import subprocess
import threading
from enum import IntEnum, StrEnum, auto
from typing import Callable, Self

from .counter import Counter


class CommandResultLevel(IntEnum):
    OK = 0
    ERROR = 1
    CRITICAL = 2


class CommandResult:
    level: CommandResultLevel
    msg: str
    additional_info: list

    def __init__(self, level: CommandResultLevel, msg: str, additional_info=None):
        self.level = level
        self.msg = msg
        if additional_info is None:
            additional_info = []
        self.additional_info = additional_info

    @staticmethod
    def new_ok(msg: str, additional_info=None):
        return CommandResult(CommandResultLevel.OK, msg, additional_info)

    @staticmethod
    def new_error(msg: str, additional_info=None):
        return CommandResult(CommandResultLevel.ERROR, msg, additional_info)

    @staticmethod
    def new_critical(msg: str, additional_info=None):
        return CommandResult(CommandResultLevel.CRITICAL, msg, additional_info)

    def __str__(self):
        return f"CommandResult({self.level})"

    def __repr__(self):
        return f"CommandResult({self.level.__repr__()})"


class RunnerRuntimeError(RuntimeError):

    def __init__(self, result: CommandResult, retry: int):
        self.result = result
        self.retry = retry

    def __str__(self):
        return f"RunnerRuntimeException({self.result.__str__()}, {self.retry})"

    def __repr__(self):
        return f"RunnerRuntimeException({self.result.__repr__()}, {self.retry})"


class ErrorStrategy(StrEnum):
    RESTART = auto()
    STOP = auto()
    OMIT = auto()


class BaseCommand:
    number_of_works: int
    log_level: int
    logger_name: str | None
    error_strategy: ErrorStrategy
    error_callback: Callable[[Self, CommandResult], Self | None] | None

    def __init__(self, **kwargs):
        self.logger = None
        self.log_level = int(kwargs.get("log_level", logging.INFO))
        self.logger_name = kwargs.get("logger_name", None)
        self.error_strategy = ErrorStrategy(
            kwargs.get("error_strategy", "stop").lower()
        )

    def process(self):
        # TODO: implement logging and record time
        result = None
        i = 1
        while i <= 3:
            try:
                result = self._do_work()
            except RunnerRuntimeError as ree:
                raise ree
            except Exception as e:
                result = CommandResult(
                    CommandResultLevel.ERROR, "Unexcepted exception caught", [e]
                )
            match result.level:
                case CommandResultLevel.OK:
                    self._increment_counter()
                    return result
                case CommandResultLevel.ERROR:
                    match self.error_strategy:
                        case ErrorStrategy.OMIT:
                            # TODO: log omitting
                            return result
                        case ErrorStrategy.RESTART:
                            # TODO: log omitting
                            i += 1
                        case ErrorStrategy.STOP:
                            # TODO: log stop
                            return result
                case CommandResultLevel.CRITICAL:
                    raise RunnerRuntimeError(result, i)
        if result is None:
            return CommandResult.new_critical("Cannot run process. ", {"command": self})
        return result

    def _do_work(self) -> CommandResult:
        raise NotImplementedError("Subclasses must implement this method")

    def _increment_counter(self):
        Counter.increment()

    def get_number_of_works(self) -> int:
        return 1

    def _log(self, level: int, message: str):
        if self.logger is None:
            if self.logger_name:
                self.logger = logging.getLogger(self.logger_name)
            else:
                return
        if self.log_level <= level:
            self.logger.log(level, message)


class ShellCommand(BaseCommand):
    def __init__(self, cmd, cwd=None, **kwargs):
        super().__init__(**kwargs)
        self.cwd = cwd
        self.cmd = cmd

    def _do_work(self):
        process = subprocess.Popen(
            self.cmd,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        # self._log(logging.INFO,) # TODO: logging
        level = (
            CommandResultLevel.OK
            if process.returncode == 0
            else CommandResultLevel.ERROR
        )
        return CommandResult(level, stdout, [stderr])


class GroupCommand(BaseCommand):
    """
    DEVELOPMENT PENDING
    GroupCommand treats all commands as one.
    So depends on set strategy, it will retry, omit all process or throw error if one of command fails.
    It is possible to define reset callback that must have arguments BaseCommand (processed that failed) and CommandResult (result) that returns None or BaseCommand to be executed
    """

    commands: list[BaseCommand]
    reset_callback: Callable[[BaseCommand, CommandResult], None | BaseCommand] | None
    iteration: int = 0

    def __init__(self, commands=None, reset_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.commands = [] if commands is None else commands
        self.reset_callback = reset_callback

    def add_command(self, command: BaseCommand):
        self.commands.append(command)

    def set_commands(self, commands: list[BaseCommand]):
        self.commands = commands

    def get_number_of_works(self) -> int:
        return sum(command.number_of_works for command in self.commands)

    def _do_work(self):
        # TODO: log
        i = 0
        try:
            while i < len(self.commands):
                self.commands[i].process()
        except RunnerRuntimeError as rre:
            if self.reset_callback is not None:
                command = self.reset_callback(self.commands[i], rre.result)
                if command is not None:
                    command.process()
            match self.error_strategy:
                case ErrorStrategy.OMIT:
                    return
                case ErrorStrategy.STOP:
                    raise rre
                case ErrorStrategy.RESTART:
                    self.iteration += 1
                    self._do_work()


class ParallelCommand(GroupCommand):
    """
    DEVELOPMENT PENDING
    Creates two threads and run them parallelly
    """

    def __init__(self, commands: list[BaseCommand], **kwargs):
        if kwargs.get("number_of_works") is not None:
            kwargs["number_of_works"] = sum(
                command.number_of_works for command in commands
            )
        super().__init__(**kwargs)
        self.commands = commands

    def _do_work(self):
        threads = []
        for command in self.commands:
            thread = threading.Thread(target=command.process)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()  # TODO: get results and output


class CyclicCommand(BaseCommand):
    """
    DEVELOPMENT PENDING
    Handles jobs that should be run more than once
    """

    def __init__(self, command: BaseCommand, cycles: int, **kwargs):
        if kwargs.get("number_of_works") is not None:
            kwargs["number_of_works"] = command.number_of_works * cycles
        super().__init__(**kwargs)
        self.command = command
        self.cycles = cycles

    def _do_work(self):
        for _ in range(self.cycles):
            self.command.process()  # TODO: handle error


class ThreadCommand(BaseCommand):
    args: list = []

    def __init__(self, command, args=None, **kwargs):
        super().__init__(**kwargs)
        if args is None:
            args = []
        self.cmd = command
        self.args = args

    def _do_work(self):
        thread = threading.Thread(target=self.cmd, args=self.args)
        thread.start()
        thread.join()


class ConditionCommand(BaseCommand):
    pass
