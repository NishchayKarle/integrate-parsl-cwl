cwlVersion: v1.0
class: CommandLineTool

baseCommand: cat

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  output_file1:
    type: File
    outputBinding:
      glob: output_file1.txt
