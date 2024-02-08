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


class CommandLineTool:
    def __init__(self, cwl_file: str) -> None:
        """Command Line Tool

        Args:
            cwl_file (str): CWL specs file for the Command Line Tool
        """
        try:
            with open(cwl_file, "r") as cwl_file:
                cwl = yaml.safe_load(cwl_file)

        except Exception as exp:
            raise Exception(exp)

        try:
            self.validate_cwl(cwl)

        except Exception as exp:
            raise Exception(exp, "Invalid CWL file")

        self.__file = cwl_file
        self.__cwl = cwl
        self.__version = self.__cwl["cwlVersion"]
        self.__base_command = None
        self.__inputs: List[InputArgument] = None
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
    def validate_cwl(cls, cwl_content: dict[str, any]) -> dict[str, any]:
        """Check if CWL is valid.

        Args:
            cwl_content (Dict[str, Any]): CWL file for the command

        Raises:
            schema.SchemaError if CWL is invalid

        Returns:
            Dict[str, Any]: Original CWL contents if valid
        """
        from schema import Schema, And, Optional, Or, Regex, Forbidden

        input_binding_schema = And(
            Schema(
                {
                    Optional("position"): int,
                    Optional("prefix"): str,
                    Optional("separate"): bool,
                    Optional("itemSeparator"): str,
                },
            ),
            len,
            error="empty inputBinding",
        )

        input_simple_types = ["boolean", "int", "long", "float", "double", "string", "File", "Directory"]
        input_array_types = [f"{t}[]" for t in input_simple_types]
        input_optional_types = [f"{t}?" for t in input_simple_types]

        input_types_schema = Or(
            *input_simple_types,
            *input_array_types,
            *input_optional_types,
            {"type": "array", "items": input_simple_types},
            error=(
                "Invalid type for input."
                "Should be one of boolean, int, long, float, double, string, File, Directory."
                "Can be optional or array of these types"
            ),
        )

        output_types_schema = Or(
            "stdout",
            "stderr",
            "File",
            "File[]",
            {"type": "array", "items": "File"},
            error="Invalid type for output. Should be stdout, stderr or File",
        )

        cwl_schema = Schema(
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
                            error="Invalid 'id'. Please use values that satisfy python variable name requirements",
                        ): Schema(
                            {
                                "type": input_types_schema,
                                Optional("default"): Or(int, float, str, bool, list, error="Invalid default value"),
                                Optional("inputBinding"): input_binding_schema,
                            }
                        ),
                    },
                    And(
                        [
                            Schema(
                                {
                                    "id": Regex(
                                        r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                                        error=(
                                            "Invalid 'id'."
                                            "Please use values that satisfy python variable name requirements"
                                        ),
                                    ),
                                    "type": input_array_types,
                                    Optional("default"): Or(int, float, str, bool, list, error="Invalid default value"),
                                    Optional("inputBinding"): input_binding_schema,
                                }
                            ),
                        ],
                        len,
                        error="Invalid List/Empty List",
                    ),
                    error="Invalid inputs.",
                ),
                Optional("outputs"): Or(
                    {str: Schema({"type": output_types_schema})},
                    And(
                        [Schema({"id": str, "type": output_types_schema})],
                        len,
                        error="Invalid List/Empty List",
                    ),
                    error="Invalid outputs",
                ),
                Optional(any): any,
            },
        )

        return cwl_schema.validate(cwl_content)

    def __set_inputs(self, cwl_inputs: Union[List[Dict[str, Any]], Dict[str, any]]) -> None:
        """Set input options from CWL

        Args:
            cwl_inputs (Union[List[Dict[str, Any]], Dict[str, any]]): CWL inputs
        """
        inputs = []

        def process_input(id, inpt):
            type = inpt["type"].rstrip("[]").rstrip("?")
            array = "[]" in inpt["type"]
            optional = "?" in inpt["type"]
            default = inpt.get("default", None)
            position = inpt.get("inputBinding", {}).get("position", None)
            prefix = inpt.get("inputBinding", {}).get("prefix", None)
            item_separator = inpt.get("inputBinding", {}).get("itemSeparator", None)
            separate = inpt.get("inputBinding", {}).get("separate", True)

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
            inputs.extend(process_input(inpt["id"], inpt) for inpt in cwl_inputs)

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

    def get_parsl_command_args(self, **kwargs) -> str:
        """Args needed to run the command using Parsl

        kwargs: input parameters, output parameters, stdout, stderr

        Returns:
            str: string of the shell command that is to be run
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
        """Local run of the command"""
        print("RESULT OF RUNNING COMMAND LINE TOOL:")
        exit_code = os.system(self.get_command(**kwargs))
        print(f"EXIT CODE: {exit_code}")
