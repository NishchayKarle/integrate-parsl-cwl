import yaml
import os
from typing import Dict, Any, Optional, List, Union
import pprint
from collections import namedtuple


class InputArgument:
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
        array: bool = False,
        optional: bool = False,
        default: Optional[Any] = None,
        position: Optional[int] = None,
        prefix: Optional[str] = None,
        item_separator: Optional[str] = None,
        separate: bool = True,
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
            input_arg_str += f"{itm_sep}".join([f"{string_quote}{arg}{string_quote}" for arg in input_arg])

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


OutputArgument = namedtuple("Output", ["id", "type", "array"])


class CommandLineTool:
    def __init__(self, cwl_file: str) -> None:
        """Command Line Tool

        Args:
            cwl_file (str): CWL specs file for the Command Line Tool
        """

        with open(cwl_file, "r") as cwl_file:
            cwl = yaml.safe_load(cwl_file)

        self.validate_cwl(cwl)

        self.__file = cwl_file
        self.__cwl = cwl
        self.__version = self.__cwl["cwlVersion"]
        self.__base_command = None
        self.__inputs: List[InputArgument] = None
        self.__outputs: List[OutputArgument] = None

        self.__set_cwl_args__()

    def __set_cwl_args__(self) -> None:
        if isinstance(self.__cwl["baseCommand"], list):
            self.__base_command = " ".join(self.__cwl["baseCommand"])
        else:
            self.__base_command = self.__cwl["baseCommand"]

        self.__set_inputs(self.__cwl["inputs"])
        if "outputs" in self.__cwl:
            self.__set_outputs(self.__cwl["outputs"])

    def __str__(self) -> str:
        return pprint.pformat(self.__cwl)

    def __call__(self, **kwargs: Any):
        """Run the CWL CommandLineTool using Parsl

        Expects: input and output arguments mentioned in the CWL file

        Make sure to use the same names for function parameters as the input and output arguments in the CWL file.
        """
        from parsl.app.app import bash_app

        @bash_app
        def __parsl_bash_app__(
            command: str,
            stdout: str = None,
            stderr: str = None,
            inputs: list = [],
            outputs: list = [],
        ) -> str:
            return command

        args = self.__get_parsl_bash_app_args(**kwargs)
        return __parsl_bash_app__(**args)

    @classmethod
    def validate_cwl(cls, cwl_content: Dict[str, any]) -> Dict[str, any]:
        """Check if CWL is valid.

        Args:
            cwl_content (Dict[str, Any]): CWL file for the command

        Raises:
            schema.SchemaError if CWL is invalid

        Returns:
            Dict[str, Any]: Original CWL contents if valid
        """
        from schema import Schema, And, Optional, Or, Regex, SchemaError

        input_binding_schema = And(
            {
                Optional("position"): int,
                Optional("prefix"): str,
                Optional("separate"): bool,
                Optional("itemSeparator"): str,
            },
            len,
            error="Empty inputBinding.",
        )

        input_simple_types = ["array", "boolean", "int", "long", "float", "double", "string", "File", "Directory"]
        input_array_types = [f"{t}[]" for t in input_simple_types]
        input_optional_types = [f"{t}?" for t in input_simple_types]

        input_types_schema = Or(
            *input_simple_types,
            *input_array_types,
            *input_optional_types,
            error=(
                "Invalid type for input."
                "Should be one of array, boolean, int, long, float, double, string, File, Directory."
                "Can be optional or array of these types"
            ),
        )

        output_types_schema = Or(
            "stdout",
            "stderr",
            "File",
            "File[]",
            "array",
            error="Invalid type for output. Should be stdout, stderr, File, File[] or array with items of type File",
        )

        cmd_line_tool_schema = Schema(
            {
                "cwlVersion": Regex(r"^v[0-9]+(\.[0-9]+){0,2}$", error="Invalid CWL Version"),
                "baseCommand": Or([str], str, error="Invalid type for Base Command"),
                "class": And(
                    str,
                    lambda cls: cls == "CommandLineTool",
                    error="Invalid type for class. Should be 'CommandLineTool'.",
                ),
                "inputs": Or(
                    {
                        Regex(
                            r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                        ): {
                            "type": input_types_schema,
                            Optional("items"): Or(*input_simple_types),
                            Optional("default"): Or(int, float, str, bool, list, error="Invalid default value"),
                            Optional("inputBinding"): input_binding_schema,
                        }
                    },
                    [
                        {
                            "id": Regex(
                                r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                            ),
                            "type": input_simple_types,
                            Optional("items"): Or(*input_simple_types),
                            Optional("default"): Or(int, float, str, bool, list, error="Invalid default value"),
                            Optional("inputBinding"): input_binding_schema,
                        }
                    ],
                    error=("Invalid/Empty 'inputs'."),
                ),
                "outputs": Or(
                    {
                        Regex(
                            r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                        ): {
                            "type": output_types_schema,
                            Optional("items"): "File",
                            Optional("outputBinding"): any,
                        }
                    },
                    [
                        {
                            "id": Regex(
                                r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                            ),
                            "type": output_types_schema,
                            Optional("items"): "File",
                            Optional("outputBinding"): any,
                        }
                    ],
                    error=("Invalid/Empty 'outputs'."),
                ),
                Optional(any): any,
            },
        )

        try:
            return cmd_line_tool_schema.validate(cwl_content)

        except SchemaError as e:
            raise Exception(
                "Invalid Cwl File for Command Line Tools\n" + "\n".join({exp for exp in e.errors if exp})
            ) from None

    def __set_inputs(self, cwl_inputs: Union[List[Dict[str, Any]], Dict[str, any]]) -> None:
        """Set input options from CWL

        Args:
            cwl_inputs (Union[List[Dict[str, Any]], Dict[str, any]]): CWL inputs
        """
        inputs = []

        def process_input(id, input_arg):
            if input_arg["type"] == "array":
                type = input_arg["items"]
                array = True

            else:
                type = input_arg["type"].rstrip("[]").rstrip("?")
                array = "[]" in input_arg["type"]

            optional = "?" in input_arg["type"]
            default = input_arg.get("default", None)
            position = input_arg.get("inputBinding", {}).get("position", None)
            prefix = input_arg.get("inputBinding", {}).get("prefix", None)
            item_separator = input_arg.get("inputBinding", {}).get("itemSeparator", None)
            separate = input_arg.get("inputBinding", {}).get("separate", True)

            return InputArgument(
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

        if isinstance(cwl_inputs, list):
            inputs.extend(process_input(input_arg["id"], input_arg) for input_arg in cwl_inputs)

        elif isinstance(cwl_inputs, dict):
            inputs.extend(process_input(id, inpt_arg_opts) for id, inpt_arg_opts in cwl_inputs.items())

        inputs.sort()
        self.__inputs = inputs

    def __set_outputs(self, cwl_outputs: Union[List[Dict[str, Any]], Dict[str, any]]) -> None:
        """Set output options from CWL

        Args:
            cwl_outputs (Union[List[Dict[str, Any]], Dict[str, any]]): CWL outputs
        """
        outputs = []

        def process_output(id, output_arg):
            type = output_arg["type"]
            if type == "array":
                type = output_arg["items"]
                array = True

            else:
                type = output_arg["type"].rstrip("[]")
                array = "[]" in output_arg["type"]

            return OutputArgument(id, type, array)

        if isinstance(cwl_outputs, list):
            outputs.extend(process_output(output_arg["id"], output_arg) for output_arg in cwl_outputs)

        elif isinstance(cwl_outputs, dict):
            outputs.extend(process_output(id, output_arg_opts) for id, output_arg_opts in cwl_outputs.items())

        self.__outputs = outputs

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

    @property
    def version(self) -> str:
        """CWL version"""
        return self.__version

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
                raise Exception(f"Input parameter(s) missing: {input_arg.id}")

        return f"{self.__base_command} {' '.join(input_args)}"

    def __get_parsl_bash_app_args(self, **kwargs) -> Dict[str, Any]:
        """Args needed to run the command using Parsl

        kwargs: values for inputs and outputs mentioned in the CWL file

        Returns: Dict[str, Any]: Args needed to run the command using Parsl
        """
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
                if file.array:
                    input_files.extend([File(f) for f in kwargs[file.id]])

                else:
                    input_files.append(File(kwargs[file.id]))

        """list output files"""
        output_files = []
        for file in self.__outputs:
            if file.type == "File" and file.id in kwargs:
                if file.array:
                    output_files.extend([File(f) for f in kwargs[file.id]])

                else:
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
        """Local run of the command"""
        print("RESULT OF RUNNING COMMAND LINE TOOL:")
        exit_code = os.system(self.get_command(**kwargs))
        print(f"EXIT CODE: {exit_code}")
