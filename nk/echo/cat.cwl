cwlVersion: v1.2
class: CommandLineTool
baseCommand: cat

inputs:
  - id: file1
    type: File
    inputBinding:
      position: 1
  - id: file2
    type: File
    inputBinding:
      position: 2
  - id: file3
    type: File
    inputBinding:
      position: 3

outputs:
  - id: output
    type: stdout

stdout: output