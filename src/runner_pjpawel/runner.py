import asyncio

from .command import BaseCommand, RunnerRuntimeError
from .counter import Counter
from .progress_bar import ProgressBar


class Runner:
    commands: list[BaseCommand]
    works: int
    progress_sleep: float
    show_progress_bar: bool = True

    def __init__(
        self,
        commands: list[BaseCommand] | None = None,
        progress_sleep: float = 0.1,
        show_progress_bar: bool = True,
    ):
        if commands is None:
            self.commands = []
        else:
            self.commands = commands
        self.progress_sleep = progress_sleep
        self.show_progress_bar = show_progress_bar

    def add_command(self, command: BaseCommand):
        self.commands.append(command)

    def run_sync(self):
        """
        Allow to run in synchronous mode.
        This is only opaque for run method
        """
        asyncio.run(self.run())

    async def run(self):
        """
        Run commands with progress_bar
        :return:
        """
        num_works = self.get_num_of_works()
        if num_works == 0:
            raise NoWorksDefinedException()
        self.reset()
        if self.show_progress_bar:
            all_results = await asyncio.gather(
                self._run_progress_bar(num_works), self._run_all_commands()
            )
            result = all_results[1]
        else:
            result = await self._run_all_commands()
        # TODO: do sth with result

    def reset(self):
        Counter.reset()

    async def _run_all_commands(self):
        try:
            for command in self.commands:
                command.process()
        except RunnerRuntimeError as rre:
            print(rre)
            # TODO: write to file

    async def _run_progress_bar(self, num_works: int):
        progress_bar = ProgressBar(max_value=num_works)
        progress_bar.reset()
        while Counter.get_count() <= num_works:
            progress_bar.display()
            await asyncio.sleep(self.progress_sleep)
        progress_bar.complete()

    def set_env_vars(self):
        pass

    def get_num_of_works(self) -> int:
        return sum(command.get_number_of_works() for command in self.commands)


# Exceptions
class NoWorksDefinedException(Exception):
    pass
