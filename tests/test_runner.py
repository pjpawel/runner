import pytest

from src.runner_pjpawel import Runner
from src.runner_pjpawel.command import ShellCommand


def test_runner_sync():
    r = Runner(show_progress_bar=False)
    r.add_command(ShellCommand("uname"))

    r.run_sync()

@pytest.mark.asyncio
async def test_runner_async():
    r = Runner(show_progress_bar=False)
    r.add_command(ShellCommand("uname"))

    await r.run()