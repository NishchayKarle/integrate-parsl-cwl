from cwl import CWLApp

# Create CommandLineTool objects CWL files

cat = CWLApp("./tools/cwl_files/cat.cwl")

find = CWLApp("./tools/cwl_files/find.cwl")

touch = CWLApp("./tools/cwl_files/touch.cwl")

wc = CWLApp("./tools/cwl_files/wc.cwl")

# etc...