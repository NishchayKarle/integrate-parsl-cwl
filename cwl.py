import yaml
import os
import subprocess
from typing import Dict, Any, Optional, Union, List
import pprint
import copy
from collections import namedtuple


class CommandLineTool:
    class __InputArgument__:
        __slots__ = (
            "id",
            "type",
            "array",
            "optional",
            "default",
            "position",
            "prefix",
            "item_separator",
            "separate",
        )

        BOOLEAN = "boolean"
        DOOUBLE = "double"
        DIRECTORY = "DIRECTORY"
        FILE = "File"
        FLOAT = "float"
        INT = "int"
        LONG = "long"
        STRING = "string"

        def __init__(
            self,
            id: str,
            type: str,
            array: bool,
            optional: bool,
            default: Optional[Any],
            position: Optional[int],
            prefix: Optional[str],
            item_separator: Optional[str],
            separate: bool,
        ):
            self.id = id
            self.type = type
            self.array = array
            self.optional = optional
            self.default = default
            self.position = position
            self.prefix = prefix
            self.item_separator = item_separator
            self.separate = separate

        def __repr__(self) -> str:
            # TODO: delete
            return str({slot: getattr(self, slot) for slot in self.__slots__})

        def __str__(self) -> str:
            if self.type == self.BOOLEAN:
                return f"[{self.prefix}]"

            input_arg_str = ""
            if self.array:
                itm_sep = self.item_separator if self.item_separator else " "
                input_arg_str += f"<{self.id}_1{itm_sep}...{itm_sep}{self.id}_n>"

            else:
                input_arg_str += f"<{self.id}>"

            if self.prefix:
                sep = " " if self.separate else ""
                input_arg_str = f"{self.prefix}{sep}{input_arg_str}"

            if self.optional:
                input_arg_str = f"[{input_arg_str}]"

            return input_arg_str

        def to_string(self, input_arg: Any = None):
            if self.type == self.BOOLEAN:
                if input:
                    return f"{self.prefix}"

                else:
                    return ""

            input_arg_str = ""
            if self.type == self.STRING:
                string_quote = "'"
            else:
                string_quote = ""

            if not input_arg:
                input_arg = self.default

            if self.array:
                itm_sep = self.item_separator if self.item_separator else " "
                input_arg_str += f"{string_quote}{itm_sep}{string_quote}".join(
                    input_arg
                )

            else:
                input_arg_str += f"{string_quote}{input_arg}{string_quote}"

            if self.prefix:
                sep = " " if self.separate else ""
                input_arg_str = f"{self.prefix}{sep}{input_arg_str}"

            return input_arg_str

        def __lt__(self, other) -> bool:
            return self.position < other.position

    def __init__(self, cwl_file: str):
        with open(cwl_file, "r") as cwl_file:
            cwl = yaml.safe_load(cwl_file)

        if not self.__validate_cwl(cwl):
            raise Exception("Invalid CommandLineTool CWL file")

        self.__file = cwl_file
        self.__base_command = None
        if isinstance(cwl["baseCommand"], list):
            self.__base_command = " ".join(cwl["baseCommand"])
        else:
            self.__base_command = cwl["baseCommand"]

        self.__inputs: List[self.__InputArgument__] = []
        self.__outputs = []

        self.__set_inputs(cwl["inputs"])
        self.__set_outputs(cwl["outputs"])

    def __str__(self) -> str:
        return pprint.pformat([self.__base_command, self.__inputs, self.__outputs])

    def __validate_cwl(self, cwl_content: Dict[str, Any]) -> bool:
        # TODO: IMPLEMENT ME!
        return True

    def __set_inputs(self, cwl_inputs):
        if isinstance(cwl_inputs, list):
            for inpt in cwl_inputs:
                id = inpt["id"]
                type = inpt["type"].rstrip("[]").rstrip("?")
                array = True if "[]" in inpt["type"] else False
                optional = True if "?" in inpt["type"] else False
                default = inpt.get("default", None)
                position = inpt.get("inputBinding", {}).get("position", None)
                prefix = inpt.get("inputBinding", {}).get("prefix", None)
                item_separator = inpt.get("inputBinding", {}).get("itemSeparator", None)
                separate = inpt.get("inputBinding", {}).get("separate", True)

                self.__inputs.append(
                    self.__InputArgument__(
                        id,
                        type,
                        array,
                        optional,
                        default,
                        position,
                        prefix,
                        item_separator,
                        separate,
                    )
                )

        elif isinstance(cwl_inputs, dict):
            for id, inpt_arg_opts in cwl_inputs.items():
                type = inpt_arg_opts["type"].rstrip("[]").rstrip("?")
                array = True if "[]" in inpt_arg_opts["type"] else False
                optional = True if "?" in inpt_arg_opts["type"] else False
                default = inpt_arg_opts.get("default", None)
                position = inpt_arg_opts.get("inputBinding", {}).get("position", None)
                prefix = inpt_arg_opts.get("inputBinding", {}).get("prefix", None)
                item_separator = inpt_arg_opts.get("inputBinding", {}).get(
                    "itemSeparator", None
                )
                separate = inpt_arg_opts.get("inputBinding", {}).get("separate", True)

                self.__inputs.append(
                    self.__InputArgument__(
                        id,
                        type,
                        array,
                        optional,
                        default,
                        position,
                        prefix,
                        item_separator,
                        separate,
                    )
                )

        else:
            print("ERROR")

        self.__inputs.sort()

    def __set_outputs(self, cwl_outputs):
        self.__set_outputs = cwl_outputs

    @property
    def command_template(self) -> str:
        return f"COMMAND TEMPLATE:\n{self.__base_command} {' '.join([str(input_arg) for input_arg in self.__inputs])}"

    def get_command(self, **kwargs):
        # TODO: handle case where kwargs has unnecessary args ?
        args = []
        for input_arg in self.__inputs:
            if input_arg.id in kwargs:
                args.append(input_arg.to_string(kwargs[input_arg.id]))

            elif input_arg.default:
                args.append(input_arg.to_string())
            
            elif input_arg.optional:
                continue

            else:
                raise Exception(f"Input parameter(s) missing: {input_arg.id}")

        return f"{self.__base_command} {' '.join(args)}"

    def run(self, **kwargs):
        # local testing run function
        print("RESULT OF RUNNING COMMAND LINE TOOL:")
        exit_code = os.system(self.get_command(**kwargs))
        print(f"EXIT CODE: {exit_code}")

class Workflow:
    def __init__(self, cwl: Dict[str, Any]) -> None:
        self.cmds = []
        self.inputs = []
        self.outputs = []
        self.steps = []

        self.__extract_commands_from_cwl(cwl)
        self.__set_inputs(cwl["inputs"])
        self.__set_outputs(cwl["outputs"])

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

    with open(os.path.join(path, cwl), "r") as cwl_file:
        cwl_content = yaml.safe_load(cwl_file)

        # Check if CWL file is a CommandLineTool
        if "class" in cwl_content and cwl_content["class"] == "CommandLineTool":
            cmdlinetool = CommandLineTool(cwl_content)
            return [cmdlinetool]

        # Check if CWL file is a Workflow
        elif "class" in cwl_content and cwl_content["class"] == "Workflow":
            # Extract the base command from the first step
            for step, todo in cwl_content.get("steps", {}).items():
                if step:
                    run_cwl = todo.get("run", "")
                    if isinstance(run_cwl, str):
                        cmdlinetool = extract_commands_from_cwl(run_cwl, path)
                    cmds.extend(cmdlinetool)
        else:
            raise Exception("ERROR")

    return cmds
