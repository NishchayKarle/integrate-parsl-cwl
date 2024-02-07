# Command Line Tool app tutorial

Command Line Tool is a python app that allows you to integrate CWL 'CommandLineTool' files with parsl.

Parsl is a python parallel scripting library. 

Learn about Parsl [here](https://parsl.readthedocs.io/en/stable/index.html)

## Getting started

### Example 1: echo.cwl

```yml
cwlVersion: v1.0
class: CommandLineTool

baseCommand: echo

inputs:
  message:
    type: string
    inputBinding:
      position: 1

outputs:
  stdout:
    type: stdout
```

### Creating a CommandLineTool app
```python
from cwl import CommandLineTool

# app takes one argument - path to cwl file
echo = CommandLineTool("echo.cwl")
print(echo.command_template)
```

### Output
```bash
COMMAND TEMPLATE:
echo <message>
```

---

### Example 2: Running the CWL locally
Running the app locally will run the command line tool on the local system, and act the same as running on a bash shell.

The arguments to the function will have the same names as the inputs and outputs listed on the CWL
```python
echo = CommandLineTool("echo.cwl")
echo.run_local(message="Hello, World!", stdout="echo_stdout.txt")
```

### Output

```bash
RESULT OF RUNNING COMMAND LINE TOOL:
Hello, World!
EXIT CODE: 0
```

---

### Running CommandLineTool app with Parsl

Parsl’s Bash app allows you to wrap execution of external applications from the command-line as you would in a Bash shell. It can also be used to execute Bash scripts directly. To define a Bash app, the wrapped Python function must return the command-line string to be executed. 

To capture stdout and stderr, the function should take arguments 'stdout' and 'stderr'. 

The input files used by the command and any output files created during execution should also be mentioned in the function arguments using arrays of parsl's File objects

Learn more about bash_app [here](https://parsl.readthedocs.io/en/stable/1-parsl-introduction.html#Bash-Apps)

### Configuring Parsl

Parsl separates code and execution. To do so, it relies on a configuration model to describe the pool of resources to be used for execution (e.g., clusters, clouds, threads).

We’ll come back to configuration later in this tutorial. For now, we configure this example to use a local pool of [threads](https://en.wikipedia.org/wiki/Thread_computing) to facilitate local parallel execution.

```python
import parsl
import os
from parsl.app.app import bash_app
from parsl.configs.local_threads import config
from parsl.data_provider.files import File

parsl.load(config)
```


Here's a generic bash_app that will work with all CommandLineTool apps

```python
@bash_app
def test(command, stdout: str = None, stderr: str = None, inputs: list[File] = [], outputs: list[File] = []):
    return command
```

### Example 1: find.cwl - cwl for the 'find' command
```yml
cwlVersion: v1.2
class: CommandLineTool
baseCommand: find

inputs:
  dir:
    type: string
    inputBinding:
      position: 1

  name:
    type: string?
    inputBinding:
      prefix: -name
      separate: true
      position: 2

  maxdepth:
    type: int?
    inputBinding:
      prefix: -maxdepth
      position: 3

outputs:
  example_out:
    type: stdout
```

```python
find = CommandLineTool("find.cwl")
print(find.command_template)
# find <dir> [-name <name>] [-maxdepth <maxdepth>]

cmd = find.get_parsl_command_args(dir=".", maxdepth=3, name="*.docx", example_out="find_stdout.txt")
"""
cmd = {
    'command': "find '.' -name '*.docx' -maxdepth 3",
    'stdout': 'find_stdout.txt',
    'stderr': None,
    'inputs': [],
    'outputs': []
}
"""

# forward args to bash_app and wait for completion
test(**cmd).result()

with open("find_stdout.txt", "r") as f:
    print(f.read())
```

```get_parsl_command_args``` function takes the same arguments as mentioned in the inputs and outputs section of the cwl and returns a python dictionary with args necessary for parsl's bash app, enabling easy forwarding of required args by bash_app.

input args with default values and optional input args in the CWL can be left out
```python
cmd = find.get_parsl_command_args(dir=".", example_out="find_stdout.txt")
"""
cmd = {
    'command': "find '.'",
    'stdout': 'find_stdout.txt',
    'stderr': None,
    'inputs': [],
    'outputs': []
}
"""

test(**cmd).result()
```
---

### Example 2: wc.cwl - cwl for 'word count' command
```yml
cwlVersion: v1.0
class: CommandLineTool
baseCommand: wc

inputs:
  text_file:
    type: File
    inputBinding:
      position: 1

outputs:
  stdout:
    type: stdout
  stderr:
    type: stderr
```

```python
wc = CommandLineTool("wc.cwl")

cmd = wc.get_parsl_command_args(text_file="test_file.txt", word_count="wc_stdout.txt")
"""
cmd = {
    'command': 'wc test_file.txt',
    'stdout': 'wc_stdout.txt',
    'stderr': 'wc_stderr.txt',
    'inputs': [<File at 0x1065d85e0 url=test_file.txt scheme=file netloc= path=test_file.txt filename=test_file.txt>],
    'outputs': []
}
"""

test(**cmd).result()
with open("wc_stdout.txt", "r") as f:
    print(f.read())
```
---

### Example 3: touch.cwl - cwl for 'touch' command
```yml
cwlVersion: v1.0
class: CommandLineTool
baseCommand: touch

inputs:
  filename:
    type: string
    inputBinding:
      position: 1

outputs:
  example_out:
    type: File
```

```python
touch = CommandLineTool("touch.cwl")
cmd = touch.get_parsl_command_args(filename="file_name_1.txt", example_out="file_name_1.txt")
"""
cmd = {
    'command': "touch 'file_name_1.txt'",
    'stdout': None,
    'stderr': None,
    'inputs': [],
    'outputs': [<File at 0x1065e22b0 url=file_name_1.txt scheme=file netloc= path=file_name_1.txt filename=file_name_1.txt>]
}
"""
test(**cmd).result()
```
---