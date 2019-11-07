import argparse

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


def run_ninja(build_name):
    pass


def parse_toml_file(parsed_toml, NinjaWriter, build_name: str, project_dir: Path):
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

    # Write all the build rules so the ninja file does not need to be rewritten each time.
    generate_build_rules(builder, project_dir, parsed_toml)

    # builds = parsed_toml["builds"]
    # the_build = find_build(build_name, builds)

    # Remember, dependencies are build in the order specified. Might need to
    # update this in the future if we ever to more complex dependency resolution.
    # requires = the_build["requires"]

    # for dependency in requires:
    #     dep_build = find_build(dependency, builds)
    #     run_ninja(dep_build)
    # builder.build(dep_build)

    # run_ninja(the_build)
    # builder.build(the_build)


def entry():
    parser = argparse.ArgumentParser(description='Aim C++ build tool.')
    parser.add_argument('--build',
                        type=str,
                        help='The build type: staticlib, dynamiclib or exe')
    parser.add_argument('--path',
                        type=str,
                        help='sum the integers (default: find the max)')

    args = parser.parse_args()
    print(args)

    project_dir = Path().cwd()
    if args.path:
        project_dir = project_dir / Path(args.path)

    ninja_path = project_dir / "build.ninja"

    toml_path = project_dir / "target.toml"
    with toml_path.open("r") as toml_file:
        with ninja_path.open("w+") as ninja_file:
            ninja_writer = Writer(ninja_file)

            parsed_toml = toml.loads(toml_file.read())
            target_schema(parsed_toml)
            parse_toml_file(parsed_toml,
                            ninja_writer,
                            args.build,
                            project_dir)


if __name__ == '__main__':
    entry()
