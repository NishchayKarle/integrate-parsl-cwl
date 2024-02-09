from cwl import CommandLineTool
import os
import parsl
from parsl.app.app import bash_app
from parsl.configs.local_threads import config

parsl.load(config)


@bash_app
def parsl_test(command, stdout: str = None, stderr: str = None, inputs: list = [], outputs: list = []):
    return command


test_cwl_files = os.path.join(os.getcwd(), "tests", "test-cwl-files")
test_runtime_files = os.path.join(os.getcwd(), "tests", "test-runtime-files")


def test_find() -> None:
    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_runtime_files, 'find_stdout_1.txt')}"
        f" {os.path.join(test_runtime_files, 'find_stdout_2.txt')}"
        f" {os.path.join(test_runtime_files, 'find_stdout_manual.txt')}"
    )

    # Run Manually
    assert (
        os.system(f"find '.' -name '*.cwl' -maxdepth 3 > {os.path.join(test_runtime_files, 'find_stdout_manual.txt')}")
        == 0
    )

    # Create CommandLineTool app and run with parsl
    find = CommandLineTool(os.path.join(test_cwl_files, "find.cwl"))

    # Test 1
    cmd1 = find.get_parsl_command_args(
        dir=".", maxdepth=3, name="*.cwl", example_out=os.path.join(test_runtime_files, "find_stdout_1.txt")
    )
    parsl_test(**cmd1).result()

    with open(os.path.join(test_runtime_files, "find_stdout_1.txt"), "r") as f1, open(
        os.path.join(test_runtime_files, "find_stdout_manual.txt"), "r"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Test 2
    cmd2 = find.get_parsl_command_args(
        dir=".", name="*.cwl", example_out=os.path.join(test_runtime_files, "find_stdout_2.txt")
    )
    parsl_test(**cmd2).result()

    with open(os.path.join(test_runtime_files, "find_stdout_2.txt"), "r") as f1, open(
        os.path.join(test_runtime_files, "find_stdout_manual.txt"), "r"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Remove Generated Files
    assert (
        os.system(
            "rm"
            f" {os.path.join(test_runtime_files, 'find_stdout_1.txt')}"
            f" {os.path.join(test_runtime_files, 'find_stdout_2.txt')}"
            f" {os.path.join(test_runtime_files, 'find_stdout_manual.txt')}"
        )
        == 0
    )


def test_find_list():
    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_runtime_files, 'find_stdout_1_list.txt')}"
        f" {os.path.join(test_runtime_files, 'find_stdout_2_list.txt')}"
        f" {os.path.join(test_runtime_files, 'find_stdout_manual_list.txt')}"
    )

    # Run Manually
    assert (
        os.system(
            f"find '.' -name '*.cwl' -maxdepth 3 > {os.path.join(test_runtime_files, 'find_stdout_manual_list.txt')}"
        )
        == 0
    )

    # Create CommandLineTool app and run with parsl
    find = CommandLineTool(os.path.join(test_cwl_files, "find.cwl"))

    # Test 1
    cmd1 = find.get_parsl_command_args(
        dir=".", maxdepth=3, name="*.cwl", example_out=os.path.join(test_runtime_files, "find_stdout_1_list.txt")
    )
    parsl_test(**cmd1).result()

    with open(os.path.join(test_runtime_files, "find_stdout_1_list.txt"), "r") as f1, open(
        os.path.join(test_runtime_files, "find_stdout_manual_list.txt"), "r"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Test 2
    cmd2 = find.get_parsl_command_args(
        dir=".", name="*.cwl", example_out=os.path.join(test_runtime_files, "find_stdout_2_list.txt")
    )
    parsl_test(**cmd2).result()

    with open(os.path.join(test_runtime_files, "find_stdout_2_list.txt"), "r") as f1, open(
        os.path.join(test_runtime_files, "find_stdout_manual_list.txt"), "r"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Remove Generated Files
    assert (
        os.system(
            "rm"
            f" {os.path.join(test_runtime_files, 'find_stdout_1_list.txt')}"
            f" {os.path.join(test_runtime_files, 'find_stdout_2_list.txt')}"
            f" {os.path.join(test_runtime_files, 'find_stdout_manual_list.txt')}"
        )
        == 0
    )


def test_touch() -> None:
    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_runtime_files, 'touch1.txt')}"
        f" {os.path.join(test_runtime_files, 'touch2.txt')}"
    )

    # Create CommandLineTool app and run with parsl
    touch = CommandLineTool(os.path.join(test_cwl_files, "touch.cwl"))

    # Test 1
    cmd1 = touch.get_parsl_command_args(
        filenames=[
            os.path.join(test_runtime_files, "touch1.txt"),
            os.path.join(test_runtime_files, "touch2.txt"),
        ],
        output_files=[
            os.path.join(test_runtime_files, "touch1.txt"),
            os.path.join(test_runtime_files, "touch2.txt"),
        ],
    )
    parsl_test(**cmd1).result()

    assert (
        os.system(
            f"[ -f {os.path.join(test_runtime_files, 'touch1.txt')} -a"
            f" -f {os.path.join(test_runtime_files, 'touch2.txt')} ]"
            " && exit 0 || exit 1"
        )
        == 0
    )

    # Remove Generated Files
    assert (
        os.system(
            "rm"
            f" {os.path.join(test_runtime_files, 'touch1.txt')}"
            f" {os.path.join(test_runtime_files, 'touch2.txt')}"
        )
        == 0
    )


def test_word_count() -> None:
    # Remove Prev Generated Files if Present
    os.system(
        "rm -rf"
        f" {os.path.join(test_runtime_files, 'word_count_stdout.txt')}"
        f" {os.path.join(test_runtime_files, 'word_count_stdout_manual.txt')}"
    )

    # Run Manually
    assert (
        os.system(
            f"wc {os.path.join(test_cwl_files, 'wc.cwl')}"
            f" > {os.path.join(test_runtime_files, 'word_count_stdout_manual.txt')}"
        )
        == 0
    )

    # Create CommandLineTool app and run with parsl
    word_count = CommandLineTool(os.path.join(test_cwl_files, "wc.cwl"))

    # Test 1
    cmd1 = word_count.get_parsl_command_args(
        text_file=os.path.join(test_cwl_files, "wc.cwl"),
        stdout=os.path.join(test_runtime_files, "word_count_stdout.txt"),
    )
    parsl_test(**cmd1).result()

    with open(os.path.join(test_runtime_files, "word_count_stdout.txt"), "r") as f1, open(
        os.path.join(test_runtime_files, "word_count_stdout_manual.txt"), "r"
    ) as f2:
        assert f1.readlines() == f2.readlines()

    # Remove Generated Files
    assert (
        os.system(
            "rm"
            f" {os.path.join(test_runtime_files, 'word_count_stdout.txt')}"
            f" {os.path.join(test_runtime_files, 'word_count_stdout_manual.txt')}"
        )
        == 0
    )
