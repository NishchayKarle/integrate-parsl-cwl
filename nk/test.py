from cwl import *

cwl_file1 = 'workflow.cwl'

# cwl_file1 = 'echo/echo.cwl'
# yml_file1 = 'echo/echo.yml'

# with open(cwl_file1, 'r') as cwl_file:
#     cwl_content = yaml.safe_load(cwl_file)

# with open(yml_file1, 'r') as yml_file:
#     yml_content = yaml.safe_load(yml_file)


# print(cwl_content)
# print()
# print(yml_content)

# echo = CommandLineTool(cwl_content, yml_content)
# print(f"command to run: {echo.command}")
# echo.run(message='abcd')


# cat = CommandLineTool(cwl_content, yml_content)
# print(cat.command)
# print(cat.run(file1='file1.txt', file2='file2.txt', file3='file3.txt'))

cmds = extract_commands_from_cwl(cwl=cwl_file1, path="./workflow")
for cmd in cmds:
    print(cmd.command)
