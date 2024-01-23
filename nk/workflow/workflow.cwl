cwlVersion: v1.0
class: Workflow

inputs:
  input_file1: File
  input_file2: File

outputs:
  output_file: File

steps:
  step1:
    run: tool1.cwl
    inputs:
      input_file: input_file1
    outputs: [output_file1]

  step2:
    run: tool2.cwl
    inputs:
      input_file: step1/output_file1
      another_input: input_file2
    outputs: [output_file]

