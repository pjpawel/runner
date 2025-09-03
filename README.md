# runner (runner-pjpawel)
Universal runner with builder objects to run async, threaded or group commands

*Build for my research projects to run multiple scenarios with retry with one command*

### Install
```shell
pip install runner
```

### Build runner
1. Create Runner class.
2. Add commands. Use prepared `Command` classes in `runner.commands` module or classes that extends `runnner.command.BaseCommand`
3. Invoke `run` or `run_sync` method.


