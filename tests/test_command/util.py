from src.runner_pjpawel.command.base import (
    BaseCommand,
    CommandResult,
    RunnerRuntimeError,
)


class RuntimeExceptionCommand(BaseCommand):

    def _do_work(self) -> CommandResult | None:
        raise RunnerRuntimeError(CommandResult.new_error(), 5)
