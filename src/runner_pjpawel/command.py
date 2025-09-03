import logging
import subprocess
import threading
import os
from enum import IntEnum
from typing import Callable

from .counter import Counter
from .error import RunnerRuntimeError


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



class BaseCommand:
    number_of_works: int

    def __init__(self, **kwargs):
        self.number_of_works = int(kwargs.get("number_of_works", 1))
        self.log_level = int(kwargs.get("log_level", logging.WARNING))
        # Additional logging

    def process(self):
        # TODO: implement logging and processing
        i = 1
        while i <= 3:
            try:
                result = self._do_work()
            except RunnerRuntimeError as ree:
                raise rre
            except Exception as e:
                result = CommandResult(CommandResultLevel.ERROR, "Unexcepted exception caught", [e])
            match result.level:
                case CommandResultLevel.OK:
                    self._increment_counter()
                    return
                case CommandResultLevel.ERROR:
                    i += 1
                case CommandResultLevel.CRITICAL:
                    raise RunnerRuntimeError(result, i)


    def _do_work(self) -> CommandResult:
        raise NotImplementedError("Subclasses must implement this method")

    def _increment_counter(self):
        Counter.increment()

    def _get_error_strategy(self):
        pass
        


class ShellCommand(BaseCommand):
    def __init__(self, cmd, **kwargs):
        super().__init__(**kwargs)
        self.cmd = cmd

    def _do_work(self):
        process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate() # TODO write to log
        level = CommandResultLevel.OK if process.returncode == 0 else CommandResultLevel.ERROR
        return CommandResult(level, stdout, [stderr])


class GroupCommand(BaseCommand):
    """
    GroupCommand treats all commands as one.
    So depends on set strategy, it will retry, omit all process or throw error if one of command fails.
    It is possible to define reset callback that must have arguments BaseCommand (processed that failed) and CommandResult (result) that returns None or BaseCommand to be executed
    """
    commands: list[BaseCommand]
    reset_callback: Callable[[BaseCommand, CommandResult], None|BaseCommand]

    def __init__(self, commands = None, reset_callback = None, **kwargs):
        super().__init__(**kwargs)
        self.commands = [] if commands is None else commands
        self.reset_callback = reset_callback

    def add_command(self, command: BaseCommand):
        self.commands.append(command)

    def set_commands(self, commands: list[BaseCommand]):
        self.commands = commands

    def _do_work(self):
        for i in range(0,len(self.commands)):
            command = self.commands[i]
            command.process() # TODO: handle error


class CyclicCommand(BaseCommand):
    def __init__(self, command: BaseCommand, cycles: int, **kwargs):
        if kwargs.get("number_of_works") is not None:
            kwargs["number_of_works"] = command.number_of_works * cycles
        super().__init__(**kwargs)
        self.command = command
        self.cycles = cycles

    def _do_work(self):
        for _ in range(self.cycles):
            self.command.process() # TODO: handle error


class ParallelCommand(BaseCommand):
    def __init__(self, commands: list[BaseCommand], **kwargs):
        if kwargs.get("number_of_works") is not None:
            kwargs["number_of_works"] = sum(command.number_of_works for command in commands)
        super().__init__(**kwargs)
        self.commands = commands

    def _do_work(self):
        threads = []
        for command in self.commands:
            thread = threading.Thread(target=command.process)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

class ThreadCommand(BaseCommand):
    args: list = []
    def __init__(self, command, args: list = [], **kwargs):
        super().__init__(**kwargs)
        self.cmd = command
        self.args = args

    def _do_work(self):
        thread = threading.Thread(target=self.cmd, args=self.args)
        thread.start()
        thread.join()
