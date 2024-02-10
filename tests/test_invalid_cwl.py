import pytest
from cwl import CommandLineTool
import os

invalid_cwl_files = os.path.join(os.getcwd(), "tests", "invalid-cwl-files")

def test_invalid_output_type() -> None:
        with pytest.raises(Exception):
            CommandLineTool(os.path.join(invalid_cwl_files, "wc_invalid.cwl"))

def test_invalid_dict_keys() -> None:
        with pytest.raises(Exception):
            CommandLineTool(os.path.join(invalid_cwl_files, "touch_invalid.cwl"))