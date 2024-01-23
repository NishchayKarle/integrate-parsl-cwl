import yaml
import os
import subprocess
import ruamel.yaml
from typing import Dict, Any
import pprint
import copy


class CommandLineTool:
    def __init__(self, commandlinetool_cwl):
        self.baseCommand = commandlinetool_cwl["baseCommand"]
        self.inputs = []
        self.outputs = []

        self.__set_inputs(commandlinetool_cwl["inputs"])
        self.__set_outputs(commandlinetool_cwl["outputs"])

    def __repr__(self) -> str:
        return pprint.pformat([self.baseCommand, self.inputs, self.outputs])

    def __str__(self) -> str:
        return pprint.pformat([self.baseCommand, self.inputs, self.outputs])

    def __set_inputs(self, cwl_inputs):
        if isinstance(cwl_inputs, list):
            self.inputs = copy.deepcopy(cwl_inputs)

        elif isinstance(cwl_inputs, dict):
            for id, input_opts in cwl_inputs.items():
                input1 = {"id": id}
                input1.update(input_opts)
                self.inputs.append(input1)

        else:
            print("ERROR")

    def __set_outputs(self, cwl_outputs):
        self.__set_outputs = cwl_outputs

    @property
    def command(self) -> str:
        return f"{self.baseCommand} " + " ".join(
            f'<{inpt["id"]}>' for inpt in self.inputs
        )

    def run(self, **kwargs):
        result = subprocess.run(
            [self.baseCommand] + [kwargs[inpt["id"]] for inpt in self.inputs],
            capture_output=True,
            text=True,
        )
        print(f"{result.stdout=}")
        print(f"{result.stderr=}")

class Workflow:
    def __init__(self, cwl: Dict[str, Any]) -> None:
        self.cmds = []
        self.inputs = []
        self.outputs = []
        self.steps = []
        
        self.__extract_commands_from_cwl(cwl)
        self.__set_inputs(cwl['inputs'])
        self.__set_outputs(cwl['outputs'])
    
    def __set_inputs(self, cwl_inputs):
        if isinstance(cwl_inputs, list):
            self.inputs = copy.deepcopy(cwl_inputs)

        elif isinstance(cwl_inputs, dict):
            for id, input_opts in cwl_inputs.items():
                input1 = {"id": id}
                input1.update(input_opts)
                self.inputs.append(input1)

        else:
            print("ERROR")

    def __set_outputs(self, cwl_outputs):
        self.__set_outputs = cwl_outputs
    

def extract_commands_from_cwl(cwl, path):
    cmds = []
    
    with open(os.path.join(path, cwl), 'r') as cwl_file:
        cwl_content = yaml.safe_load(cwl_file)

        # Check if CWL file is a CommandLineTool
        if 'class' in cwl_content and cwl_content['class'] == 'CommandLineTool':
            cmdlinetool = CommandLineTool(cwl_content)
            return [cmdlinetool]

        # Check if CWL file is a Workflow
        elif 'class' in cwl_content and cwl_content['class'] == 'Workflow':
            # Extract the base command from the first step
            for step, todo in cwl_content.get('steps', {}).items():
                if step:
                    run_cwl = todo.get('run', '')
                    if isinstance(run_cwl, str):
                        cmdlinetool = extract_commands_from_cwl(run_cwl, path)
                    cmds.extend(cmdlinetool)
        else:
            raise Exception('ERROR')
    
    return cmds