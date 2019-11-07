import argparse
import subprocess

import toml
from ninja_syntax import Writer

from aim import gccbuilds
from aim import msvcbuilds
from aim.schema import target_schema
from aim.utils import *


def generate_build_rules(builder, project_dir, parsed_toml):
    flags = getattr(parsed_toml, "flags", [])
    defines = getattr(parsed_toml, "defines", [])
    builds = parsed_toml["builds"]
    for build_info in builds:
        build_info["directory"] = project_dir
        build_info["flags"] = flags
        build_info["defines"] = defines
        builder.build(build_info)


def find_build(build_name, builds):
    for build in builds:
        if build["name"] == build_name:
            return build
    else:
        raise RuntimeError(f"Failed to find build with name: {build_name}")


def run_ninja(working_dir, build_name):
    command = ["ninja", build_name]
    print(" ".join(command) + " ...")
    result = subprocess.run(command, cwd=str(working_dir), capture_output=True)
    if result.stdout:
        print(result.stdout.decode("utf-8"))
    if result.stderr:
        print(result.stderr.decode("utf-8"))


def parse_toml_file(parsed_toml, NinjaWriter, project_dir: Path):
    compiler_c = parsed_toml["cxx"]
    compiler_cpp = parsed_toml["cc"]
    archiver = parsed_toml["ar"]
    frontend = parsed_toml["compilerFrontend"]

    if frontend == "msvc":
        builder = msvcbuilds.MSVCBuilds(NinjaWriter,
                                        compiler_cpp,
                                        compiler_c,
                                        archiver)
    else:
        builder = gccbuilds.GCCBuilds(NinjaWriter,
                                      compiler_cpp,
                                      compiler_c,
                                      archiver)

    generate_build_rules(builder, project_dir, parsed_toml)


def entry():
    parser = argparse.ArgumentParser(description='Aim C++ build tool.')
    parser.add_argument('--build',
                        type=str,
                        required=True,
                        help='The build name')
    parser.add_argument('--path',
                        type=str,
                        help='Path to target directory')

    args = parser.parse_args()
    print(args)

    project_dir = Path().cwd()
    if args.path:
        project_dir = project_dir / Path(args.path)

    ninja_path = project_dir / "build.ninja"
    toml_path = project_dir / "target.toml"

    with toml_path.open("r") as toml_file:
        parsed_toml = toml.loads(toml_file.read())

        # Check that the build exists before doing any work.
        builds = parsed_toml["builds"]
        the_build = find_build(args.build, builds)

        with ninja_path.open("w+") as ninja_file:
            ninja_writer = Writer(ninja_file)

            target_schema(parsed_toml)
            parse_toml_file(parsed_toml,
                            ninja_writer,
                            project_dir)

        run_ninja(project_dir, the_build["name"])


if __name__ == '__main__':
    entry()
