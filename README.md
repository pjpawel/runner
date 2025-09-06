# runner (runner-pjpawel)
Universal runner with builder objects to run async, threaded or group commands

*Build for my research projects to run multiple scenarios with retry with one command*

### *Remember! This project is on early stage of development* 

### Install
```shell
pip install runner-pjpawel
```

### Build runner
1. Create Runner class.
```python
from runner_pjpawel import Runner
runner = Runner()
```
2. Add commands. Use prepared `Command` classes in `runner.commands` module or classes that extends `runnner.command.BaseCommand`
```python
from runner_pjpawel import Command
```
3. Invoke `run` or `run_sync` method.

### Build your commands



### Full example





