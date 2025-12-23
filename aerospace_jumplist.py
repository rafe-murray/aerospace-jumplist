import subprocess
from pathlib import Path
import argparse
from argparse import Namespace
import re


class Aerospace_Jumplist:
    # Directory for all of our state
    jumplist_dir = Path.home() / ".aerospace_jumplist"

    # Path to the file containing the jumplist itself. This is structured so
    # that each line contains an entry in the list, with the id of the workspace
    # corresponding to that jump
    list_path = jumplist_dir / "list"

    # Path to the file containing the head of the list. This file contains the
    # index (1-indexed to match line number) of the currently selected workspace
    # in the jumplist.
    head_path = jumplist_dir / "head"

    # Path to a file that track if the current jump is internal or initiated by
    # one of the functions in this file. This is necessary to track so that we
    # don't push and destroy our history when we navigate back in the jumplist
    is_internal_jump_path = jumplist_dir / "is_internal_jump"

    # Regex for empty file (also matches when it is just whitespace)
    empty_re = re.compile(r"\s*")

    @staticmethod
    def get_head() -> int:
        with Aerospace_Jumplist.head_path.open("r") as head_file:
            line = head_file.readline()
            if re.fullmatch(Aerospace_Jumplist.empty_re, line) is not None:
                return 0
            else:
                return int(line)

    # Add an entry to the history list. All entries after the (previous) head of the list are removed.
    @staticmethod
    def push(workspace: str):
        if Aerospace_Jumplist.is_internal_jump():
            Aerospace_Jumplist.set_is_internal_jump(False)
            return
        head = Aerospace_Jumplist.get_head()
        lines_to_keep = []
        if head != 0:
            with Aerospace_Jumplist.list_path.open("r") as list_file:
                for i, line in enumerate(list_file, start=1):
                    lines_to_keep += line
                    if i == head:
                        break
        lines_to_keep += f"{workspace}\n"
        # TODO: if this is slow, check if we have anything in the file after head before rewriting the whole file
        with Aerospace_Jumplist.list_path.open("w") as list_file:
            list_file.writelines(lines_to_keep)
        Aerospace_Jumplist.set_head(head + 1)

    @staticmethod
    def set_head(new_head: int):
        with Aerospace_Jumplist.head_path.open("w") as head_file:
            head_file.write(f"{new_head}\n")

    @staticmethod
    def jumplist_at(index: int) -> str:
        with Aerospace_Jumplist.list_path.open("r") as list_file:
            for i, line in enumerate(list_file, start=1):
                if i == index:
                    return line
        return ""

    # Go backwards one entry in the history list. Returns the new workspace
    @staticmethod
    def go_back():
        head = Aerospace_Jumplist.get_head()
        if head > 1:
            Aerospace_Jumplist.set_head(head - 1)
            workspace = Aerospace_Jumplist.jumplist_at(head - 1)
            workspace = workspace.strip()
            Aerospace_Jumplist.set_is_internal_jump(True)
            subprocess.call(["aerospace", "workspace", workspace])

    # Go forwards one entry in the history list. Returns the new workspace
    @staticmethod
    def go_forward():
        head = Aerospace_Jumplist.get_head()
        workspace = Aerospace_Jumplist.jumplist_at(head + 1)
        if workspace != "":
            Aerospace_Jumplist.set_head(head + 1)
            workspace = workspace.strip()
            Aerospace_Jumplist.set_is_internal_jump(True)
            subprocess.call(["aerospace", "workspace", workspace])

    @staticmethod
    def is_internal_jump() -> bool:
        with Aerospace_Jumplist.is_internal_jump_path.open(
            "r"
        ) as is_internal_jump_file:
            is_internal_jump = is_internal_jump_file.readline().strip()
            # Use string comparison as bool() operator converts any non-empty string to True
            # By not explicitly checking false, the user need not initialize the file before using
            return is_internal_jump == "True"

    @staticmethod
    def set_is_internal_jump(value: bool):
        with Aerospace_Jumplist.is_internal_jump_path.open(
            "w"
        ) as is_internal_jump_file:
            is_internal_jump_file.write(f"{value}")


# Pass the arguments in args other than args.func to args.func as kwargs and run it
def run_arg_func(args: Namespace):
    filtered_args = vars(args)
    func = filtered_args.pop("func")
    func(**filtered_args)


def main():
    parser = argparse.ArgumentParser(
        description="Manage Aerospace workspace history using a vim-like jumplist"
    )
    subparsers = parser.add_subparsers(required=True)
    push_parser = subparsers.add_parser(
        "push",
        help="Add an entry to the jumplist. All entries after the (previous) head of the list are removed",
    )
    push_parser.add_argument(
        "workspace",
        type=str,
        help="The name of the workspace as seen in Aerospace e.g. '1' or 'a'",
    )
    push_parser.set_defaults(func=Aerospace_Jumplist.push)

    back_parser = subparsers.add_parser(
        "go-back",
        help="Go backwards one entry in the jumplist",
    )
    back_parser.set_defaults(func=Aerospace_Jumplist.go_back)

    forward_parser = subparsers.add_parser(
        "go-forward",
        help="Go forwards one entry in the jumplist",
    )
    forward_parser.set_defaults(func=Aerospace_Jumplist.go_forward)

    args = parser.parse_args()
    run_arg_func(args)


if __name__ == "__main__":
    main()
