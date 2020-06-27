import argparse
import subprocess

import toml

from aim import gccbuilds
from aim import msvcbuilds
from aim.schema import target_schema
from aim.utils import *
from aim.version import __version__


def generate_build_rules(builder, project_dir, parsed_toml):
    flags = parsed_toml.get("flags", [])
    defines = parsed_toml.get("defines", [])
    builds = parsed_toml["builds"]
    for build_info in builds:
        build_info["directory"] = project_dir
        build_info["flags"] = flags
        build_info["defines"] = defines
        builder.build(build_info, parsed_toml)


def find_build(build_name, builds):
    for build in builds:
        if build["name"] == build_name:
            return build
    else:
        raise RuntimeError(f"Failed to find build with name: {build_name}")


def run_ninja(working_dir, build_name):
    command = ["ninja", f"-C{build_name}", build_name]
    command_str = " ".join(command)
    print(f"Executing \"{command_str}\"")
    # TODO IMPROVEMENT - we should poll the output of ninja.
    result = subprocess.run(command, cwd=str(working_dir), capture_output=True)
    if result.stdout:
        print(result.stdout.decode("utf-8"))
    if result.stderr:
        print(result.stderr.decode("utf-8"))


def parse_toml_file(parsed_toml, project_dir: Path):
    compiler_c = parsed_toml["cc"]
    compiler_cpp = parsed_toml["cxx"]
    archiver = parsed_toml["ar"]
    frontend = parsed_toml["compilerFrontend"]

    if frontend == "msvc":
        builder = msvcbuilds.MSVCBuilds(compiler_cpp,
                                        compiler_c,
                                        archiver)
    else:
        builder = gccbuilds.GCCBuilds(compiler_cpp,
                                      compiler_c,
                                      archiver)

    generate_build_rules(builder, project_dir, parsed_toml)


def entry():
    # TODO: Get version automatically from the pyproject.toml file.
    parser = argparse.ArgumentParser(description=f"Version {__version__}")

    parser.add_argument("-v", "--version", action="version", version=__version__)
    sub_parser = parser.add_subparsers(dest="command", help="Commands")
    init_parser = sub_parser.add_parser("init", help="Initialise the current directory")

    build_parser = sub_parser.add_parser("build", help="The build name")
    build_parser.add_argument('--target',
                              type=str,
                              required=True,
                              help='The build target name')

    build_parser.add_argument('--path',
                              type=str,
                              help='Path to target directory')

    args = parser.parse_args()
    mode = args.command
    if mode == "init":
        run_init()
    elif mode == "build":
        run_build(args.target, args.path)
    else:
        import sys
        parser.print_help(sys.stdout)


WindowsDefaultTomlFile = """\
cxx = "clang-cl"
cc = "clang-cl"
ar = "llvm-ar"
compilerFrontend="msvc"

flags = [
    "/std:c++17",
    "/Zi",
]

defines = []

#[[builds]]
#    name = "static"
#    buildRule = "staticlib"
#    outputName = "libraryName.lib"
#    srcDirs = ["../lib"]
#    includePaths = ["../include"]

[[builds]]
    name = "shared"
    buildRule = "dynamiclib"
    outputName = "libraryName.dll"
    srcDirs = ["../lib"]
    includePaths = ["../include"]

[[builds]]
    name = "exe"
    requires= ["shared"]
    buildRule = "exe"
    outputName = "exeName.exe"
    srcDirs = ["../app"]
    includePaths = ["../lib"]
    libraryPaths = ["./shared"]
    libraries = [""]
"""

LinuxDefaultTomlFile = """\
projectRoot = "../.."

cxx = "clang++"
cc = "clang"
ar = "ar"
compilerFrontend="gcc"

flags = [
    "-std=c++17",
    "-g"
]

defines = []

[[builds]]                              # a list of builds.
    name = "lib_calculator"             # the unique name for this build.
    buildRule = "staticlib"             # the type of build, in this case create a static library.
    outputName = "libCalculator.a"      # the library output name,
    srcDirs = ["lib"]                   # the src directories  to build the static library from.
    includePaths = ["include"]    # additional include paths to use during the build.

#[[builds]]
#    name = "lib_calculator_so"         # the unique name for this build.
#    buildRule = "dynamiclib"           # the type of build, in this case create a shared library.
#    outputName = "libCalculator.so"    # the library output name,
#    srcDirs = ["lib"]                  # the src directories to build the shared library from.
#    includePaths = ["include"]         # additional include paths to use during the build.

[[builds]]
    name = "exe"                        # the unique name for this build.
    buildRule = "exe"                   # the type of build, in this case an executable.
    requires = ["lib_calculator"]       # build dependencies. Aim figures out the linker flags for you.
    outputName = "the_calculator.exe"   # the exe output name,
    srcDirs = ["src"]                   # the src directories to build the shared library from.
    includePaths = ["include"]          # additional include paths to use during the build.
    #libraryPaths = []                   # additional library paths, used for including third party libraries.
    #libraries = []                      # additional libraries, used for including third party libraries.
"""

CALCULATOR_CPP = """\
#include "calculator.h"

float add(float x, float y)
{
    return x + y;
}
"""

CALCULATOR_H = """\
#ifndef CALCULATOR_H
#define CALCULATOR_H

float add(float x, float y);

#endif
"""

MAIN_CPP = """\
#include "calculator.h"
#include <stdio.h>

int main()
{
    float result = add(40, 2);
    printf("The result is %f\\n", result);
    return 0;
}
"""


def run_init():
    project_dir = Path().cwd()
    dirs = ["include", "src", "lib", "builds"]
    dirs = [project_dir / x for x in dirs]
    print(f"Creating directories...")
    for a_dir in dirs:
        print(f"\t{str(a_dir)}")
        a_dir.mkdir(exist_ok=True)

    windows_targets = [
        "windows-clang_cl-debug",
        "windows-clang_cl-release",
    ]

    linux_targets = [
        "linux-clang++-debug",
        "linux-clang++-release"
    ]

    print("Creating common build targets...")
    build_dir = project_dir / "builds"
    for target in windows_targets:
        target_dir = build_dir / target
        target_dir.mkdir(exist_ok=True)
        # print(f"\t{str(target_dir)}")

        toml_file = target_dir / "target.toml"
        toml_file.touch(exist_ok=True)
        print(f"\t{str(toml_file)}")

        toml_file.write_text(WindowsDefaultTomlFile)

    for target in linux_targets:
        target_dir = build_dir / target
        target_dir.mkdir(exist_ok=True)
        # print(f"\t{str(target_dir)}")

        toml_file = target_dir / "target.toml"
        toml_file.touch(exist_ok=True)
        print(f"\t{str(toml_file)}")

        toml_file.write_text(LinuxDefaultTomlFile)

    (dirs[0] / "calculator.h").write_text(CALCULATOR_H)
    (dirs[1] / "main.cpp").write_text(MAIN_CPP)
    (dirs[2] / "calculator.cpp").write_text(CALCULATOR_CPP)


def run_build(build_name, target_path):
    project_dir = Path().cwd()

    if target_path:
        target_path = Path(target_path)
        if target_path.is_absolute():
            project_dir = target_path
        else:
            project_dir = project_dir / Path(target_path)

    # ninja_path = project_dir / "build.ninja"
    toml_path = project_dir / "target.toml"

    with toml_path.open("r") as toml_file:
        parsed_toml = toml.loads(toml_file.read())

        # Check that the build exists before doing any work.
        builds = parsed_toml["builds"]
        the_build = find_build(build_name, builds)

        # with ninja_path.open("w+") as ninja_file:
        #     ninja_writer = Writer(ninja_file)

        root_dir = parsed_toml["projectRoot"]
        project_dir = (project_dir / root_dir).resolve()
        assert project_dir.exists(), f"{str(project_dir)} does not exist."

        try:
            target_schema(parsed_toml, project_dir)
        except RuntimeError as e:
            print(f"Error: {e.args[0]}")
            exit(-1)
        parse_toml_file(parsed_toml, project_dir)

        run_ninja(project_dir, the_build["name"])


if __name__ == '__main__':
    entry()
