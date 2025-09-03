import logging
import threading
import os
from enum import IntEnum

from .counter import Counter

class CommandResultLevel(IntEnum):
    Ok = 0
    Error = 1
    CriticalError = 2

class CommandResult:
    level: CommandResultLevel

    def __init__(self, level: CommandResultLevel = 0):
        self.level = level



class BaseCommand:
    number_of_works: int

    def __init__(self, **kwargs):
        self.number_of_works = int(kwargs.get("number_of_works", 1))
        self.log_level = int(kwargs.get("log_level", logging.WARNING))

    def process(self):
        # TODO: implement logging and processing
        result = self._do_work()
        if result.level == CommandResultLevel.Ok:
            self._increment_counter()

    def _do_work(self) -> CommandResult:
        raise NotImplementedError("Subclasses must implement this method")

    def _increment_counter(self):
        Counter.increment()

    def _get_error_strategy(self):
        


class ShellCommand(BaseCommand):
    def __init__(self, cmd, **kwargs):
        super().__init__(**kwargs)
        self.cmd = cmd

    def _do_work(self):
        pass


class GroupCommand(BaseCommand):
    commands: list[BaseCommand]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.commands = []

    def add_command(self, command: BaseCommand):
        self.commands.append(command)

    def set_commands(self, commands: list[BaseCommand]):
        self.commands = commands

    def _do_work(self):
        for command in self.commands:
            command.process()


class CyclicCommand(BaseCommand):
    def __init__(self, command: BaseCommand, cycles: int, **kwargs):
        if kwargs.get("number_of_works") is not None:
            kwargs["number_of_works"] = command.number_of_works * cycles
        super().__init__(**kwargs)
        self.command = command
        self.cycles = cycles

    def _do_work(self):
        for _ in range(self.cycles):
            self.command.process()


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
        # while thread.is_alive():
        #TODO:
