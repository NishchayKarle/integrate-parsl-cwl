cwlVersion: v1.0
class: CommandLineTool

baseCommand: grep

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
  another_input:
    type: File
    inputBinding:
      position: 2

outputs:
  output_file:
    type: File
    outputBinding:
      glob: output_file.txt
