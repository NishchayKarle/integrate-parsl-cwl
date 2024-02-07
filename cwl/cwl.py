import yaml
import os
from typing import Dict, Any, Optional, List, Union
import pprint
from collections import namedtuple


class CommandLineTool:
    # TODO: add slots?
    class __InputArgument:
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
        DOUBLE = "double"
        DIRECTORY = "Directory"
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
        ) -> None:
            """Class to represent input arguments for a command line tool

            Args:
                id (str): ID of the input argument
                type (str): Type of the input argument - string, int, long, double, float, boolean, Directory, File
                array (bool): Is the type an array?
                optional (bool): Is the input argument optional?
                default (Optional[Any]): Default value for the input argument
                position (Optional[int]): Position of the input argument
                prefix (Optional[str]): Add a prefix to the input argument
                item_separator (Optional[str]): Separator for items in the array
                separate (bool): Add a space between the prefix and the input argument
            """
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
            return str({slot: getattr(self, slot) for slot in self.__slots__})

        def __str__(self) -> str:
            return str({slot: getattr(self, slot) for slot in self.__slots__})

        def to_string_template(self) -> str:
            """Template string representation of the input argument. Like [-attr=<value>]"""
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

        def to_string(self, input_arg: Any = None) -> str:
            """String representation of the input argument

            Args:
                input_arg (Any, optional): input arg value. Defaults to None.
            """
            if self.type == self.BOOLEAN:
                if input:
                    return f"{self.prefix}"

                else:
                    return ""

            input_arg_str = ""
            if not input_arg:
                input_arg = self.default

            if self.type == self.STRING:
                string_quote = "'"
            else:
                string_quote = ""

            if self.array:
                itm_sep = self.item_separator if self.item_separator else " "
                input_arg_str += f"{string_quote}{itm_sep}{string_quote}".join(input_arg)

            else:
                input_arg_str += f"{string_quote}{input_arg}{string_quote}"

            if self.prefix:
                sep = " " if self.separate else ""
                input_arg_str = f"{self.prefix}{sep}{input_arg_str}"

            return input_arg_str

        def __lt__(self, other) -> bool:
            if self.position is None and other.position is None:
                return True

            if self.position is None:
                return False

            if other.position is None:
                return True

            return self.position < other.position

    def __init__(self, cwl_file: str) -> None:
        """Command Line Tool

        Args:
            cwl_file (str): CWL specs file for the Command Line Tool

        Raises:
            #TODO: change exception types
            Exception: _description_
            Exception: _description_
        """
        try:
            with open(cwl_file, "r") as cwl_file:
                cwl = yaml.safe_load(cwl_file)

        # TODO: change exception types
        except Exception as exp:
            raise Exception(exp)

        try:
            self.validate_cwl(cwl)

        # TODO: change exception types
        except Exception as exp:
            raise Exception(exp, "Invalid CWL file")

        self.__file = cwl_file
        self.__cwl = cwl
        self.__version = self.__cwl["cwlVersion"]
        self.__base_command = None
        self.__inputs: List[self.__InputArgument] = None
        self.__outputs = None

        self.__set_cwl_args__()

    def __set_cwl_args__(self) -> None:
        if isinstance(self.__cwl["baseCommand"], list):
            self.__base_command = " ".join(self.__cwl["baseCommand"])
        else:
            self.__base_command = self.__cwl["baseCommand"]

        self.__set_inputs(self.__cwl["inputs"])
        self.__set_outputs(self.__cwl["outputs"])

    def __str__(self) -> str:
        return pprint.pformat(self.__cwl)

    @classmethod
    def validate_cwl(self, cwl_content: Dict[str, Any]) -> Dict[str, Any]:
        """Check if CWL is valid.

        Args:
            cwl_content (Dict[str, Any]): CWL file for the command

        Raises:
            schema.SchemaError if CWL is invalid

        Returns:
            Dict[str, Any]: Original CWL contents if valid
        """
        # TODO: COMPLETE ME!
        from schema import Schema, And, Optional, Or

        cwl_schema = Schema(
            {
                "cwlVersion": str,  # TODO: regex
                "baseCommand": Or([str], str, error="Invalid type for Base Command"),
                "class": And(
                    str,
                    lambda cls: cls == "CommandLineTool",
                    error="Invalid type for class. Should be 'CommandLineTool'.",
                ),
                "inputs": Or(
                    {
                        # TODO: only accept python variable name strings
                        str: Schema(
                            {
                                # TODO: valid types only
                                "type": str,
                                # TODO: check if default value matches type above
                                Optional("default"): any,
                                Optional("inputBinding"): Schema(
                                    {
                                        Optional("position"): int,
                                        Optional("prefix"): str,
                                        Optional("separate"): bool,
                                        Optional("itemSeparator"): str,
                                    }
                                ),
                            }
                        ),
                    },
                    And(
                        [
                            Schema(
                                {
                                    # TODO: only accept python variable name strings
                                    "id": str,
                                    # TODO: valid types only
                                    "type": str,
                                    # TODO: check if default value matches type above
                                    Optional("default"): Or(str, int, float, bool, list, dict, None),  # TODO:?
                                    Optional("inputBinding"): Schema(
                                        {
                                            Optional("position"): int,
                                            Optional("prefix"): str,
                                            Optional("separate"): bool,
                                            Optional("itemSeparator"): str,
                                        }
                                    ),
                                }
                            ),
                        ],
                        len,
                        error="Invalid List/Empty List. Should be a list of dicts",
                    ),
                    error="Invalid inputs. Should be a dict or list of dicts",
                ),
                Optional("outputs"): Or(
                    {
                        str: Schema(
                            {
                                "type": Or(
                                    "stdout",
                                    "stderr",
                                    "File",
                                    error="Invalid type for output. Should be stdout, stderr or File",
                                )
                            }
                        )
                    },
                    And(
                        [
                            Schema(
                                {
                                    "id": str,
                                    "type": Or(
                                        "stdout",
                                        "stderr",
                                        "File",
                                        error="Invalid type for output. Should be stdout, stderr or File",
                                    ),
                                }
                            )
                        ],
                        len,
                        error="Invalid List/Empty List",
                    ),
                    error="Invalid outputs",
                ),
            }
        )

        return cwl_schema.validate(cwl_content)

    def __set_inputs(self, cwl_inputs: Union[List[Dict[str, Any]], Dict[str, any]]) -> None:
        """Set input options from CWL

        Args:
            cwl_inputs (Union[List[Dict[str, Any]], Dict[str, any]]): CWL inputs
        """
        inputs = []
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

                inputs.append(
                    self.__InputArgument(
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
                item_separator = inpt_arg_opts.get("inputBinding", {}).get("itemSeparator", None)
                separate = inpt_arg_opts.get("inputBinding", {}).get("separate", True)

                inputs.append(
                    self.__InputArgument(
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

        inputs.sort()
        self.__inputs = inputs

    def __set_outputs(self, cwl_outputs: Union[List[Dict[str, Any]], Dict[str, any]]) -> None:
        """Set output options from CWL

        Args:
            cwl_outputs (Union[List[Dict[str, Any]], Dict[str, any]]): CWL outputs
        """
        outputs = []
        __OutputArgument = namedtuple("Output", ["id", "type"])

        if isinstance(cwl_outputs, list):
            for output in cwl_outputs:
                id = cwl_outputs["id"]
                type = cwl_outputs["type"]

                outputs.append(__OutputArgument(id, type))

        elif isinstance(cwl_outputs, dict):
            for id, output_arg_opts in cwl_outputs.items():
                type = output_arg_opts["type"]

                outputs.append(__OutputArgument(id, type))

        self.__outputs = outputs
        print(self.__outputs)

    @property
    def command_template(self) -> str:
        """Synopsis/Template for the command.

        Returns:
            str: template string to show example usage
        """
        return (
            f"COMMAND TEMPLATE:\n{self.__base_command} "
            f"{' '.join([input_arg.to_string_template() for input_arg in self.__inputs])}"
        )

    def get_command(self, **kwargs) -> str:
        """Shell command to be run.

        kwargs: input parameters

        Returns:
            str: string of the shell command that is to be run
        """
        input_args = []
        for input_arg in self.__inputs:
            if input_arg.id in kwargs:
                input_args.append(input_arg.to_string(kwargs[input_arg.id]))

            elif input_arg.default:
                input_args.append(input_arg.to_string())

            elif input_arg.optional:
                continue

            else:
                # TODO: change exception types
                raise Exception(f"Input parameter(s) missing: {input_arg.id}")

        return f"{self.__base_command} {' '.join(input_args)}"

    def get_parsl_command_args(self, **kwargs) -> str:
        """Args needed to run the command using Parsl

        kwargs: input parameters, output parameters, stdout, stderr

        Returns:
            str: string of the shell command that is to be run
        """
        # TODO: handle case where kwargs has unnecessary args ?
        cmd_args = {
            "command": None,
            "stdout": None,
            "stderr": None,
            "inputs": None,
            "outputs": None,
        }

        """get command string"""
        command = self.get_command(**kwargs)

        """Check if all the output arguments are provided"""
        stdout = None
        stderr = None
        for output_arg in self.__outputs:
            """handle stdout and stderr"""
            if output_arg.type == "stdout":
                if output_arg.id not in kwargs:
                    raise Exception("value for stdout not provided")

                else:
                    stdout = kwargs[output_arg.id]

            if output_arg.type == "stderr":
                if output_arg.id not in kwargs:
                    raise Exception("value for stderr not provided")

                else:
                    stderr = kwargs[output_arg.id]

            if output_arg.type == "File" and output_arg.id not in kwargs:
                raise Exception(f"value for output file {output_arg.id} not provided")

        from parsl.data_provider.files import File

        """list input files"""
        input_files = []
        for file in self.__inputs:
            if file.type == "File" and file.id in kwargs:
                input_files.append(File(kwargs[file.id]))

        """list output files"""
        output_files = []
        for file in self.__outputs:
            if file.type == "File" and file.id in kwargs:
                output_files.append(File(kwargs[file.id]))

        cmd_args.update(
            {
                "command": command,
                "stdout": stdout,
                "stderr": stderr,
                "inputs": input_files,
                "outputs": output_files,
            }
        )

        return cmd_args

    def run_local(self, **kwargs):
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
            self.inputs = cwl_inputs

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
