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

find(dir=".", maxdepth=3, name="*.docx", example_out="find_stdout.txt").result()

with open("find_stdout.txt", "r") as f:
    print(f.read())
```

### What's Executed:
```
$ find '.' -name '*.docx' -maxdepth 3
```

Running the CommandLineTool expects the same arguments as mentioned in the inputs and outputs section of the cwl
</br>
Args can be optional and left out and can have default values which will be used if left out

```python
find(dir=".", example_out="find_stdout.txt").result()
```

### What's Executed:
```
$ find '.'
```
---

### Example 2: wc.cwl - word count
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

wc(text_file="test_file.txt", word_count="wc_stdout.txt").result()

with open("wc_stdout.txt", "r") as f:
    print(f.read())
```

### What's Executed:
```
$ wc test_file.txt
```
---

### Example 3: touch.cwl - create files
```yml
cwlVersion: v1.0
class: CommandLineTool
baseCommand: touch

inputs:
  filenames:
    type: string[]
    inputBinding:
      position: 1
      separate: true

outputs:
  output_files:
    type: array
    items: File
    outputBinding:
      glob: $(inputs.filenames)
```

```python
touch = CommandLineTool("touch.cwl")

touch(filenames=["file_name_1.txt", "file_name_2.txt"], output_files=["file_name_1.txt", "file_name_2.txt"]).result()
```

```
$ touch 'file_name_1.txt' 'file_name_2.txt'
```
---

### Example 4: cat.cwl - Cat contents of one file to another file
```yml
cwlVersion: v1.0
class: CommandLineTool
baseCommand: cat

inputs:
  from_file:
    type: File
    inputBinding:
      position: 1
    
  to_file:
    type: string
    inputBinding:
      position: 2
      prefix: ">"
      separate: true

outputs:
  output_file:
    type: File
```

```python
cat = CommandLineTool("cat.cwl")
cat(from_file="test_file.txt", to_file="cat_stdout.txt", output_file="cat_stdout.txt").result()
```

```
$ cat test_file.txt > 'cat_stdout.txt'
```