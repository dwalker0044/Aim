import toml
import argparse
import sys
import os
from pathlib import Path
import subprocess


def release():
    toml_path = Path("pyproject.toml")
    with toml_path.open("r") as toml_file:
        parsed_toml = toml.loads(toml_file.read())

    parser = argparse.ArgumentParser(description="Tool for automating releases.")
    group = parser.add_mutually_exclusive_group()

    group.add_argument("--major", action="store_true")
    group.add_argument("--minor", action="store_true")
    group.add_argument("--micro", action="store_true")

    args = parser.parse_args()

    version = parsed_toml["tool"]["poetry"]["version"]
    version = version.split(".")
    version = tuple(int(part) for part in version)

    if args.major:
        new_version_tuple = version[0] + 1, 0, 0
    elif args.minor:
        new_version_tuple = version[0], version[1] + 1, 0
    elif args.micro:
        new_version_tuple = version[0], version[1], version[2] + 1
    else:
        parser.print_help(sys.stdout)
        return

    new_version_string = [str(part) for part in new_version_tuple]
    new_version_string = ".".join(new_version_string)

    version_path = Path("src/aim_build/version.py")
    version_info = [
        f'__version__ = "{new_version_string}"',
        f"__version_info__ = ({new_version_tuple[0]}, {new_version_tuple[1]}, {new_version_tuple[2]})",
    ]

    subprocess.run(["poetry", "version", new_version_string])

    with version_path.open("w") as version_file:
        for line in version_info:
            version_file.write(line + os.linesep)


if __name__ == "__main__":
    release()
