from typing import Dict
from pathlib import Path
from aim.utils import prepend_paths, relpath, escape_path
from aim.gccbuilds import GCCBuilds
from aim.gccbuilds import find_build, PrefixLibraryPath, PrefixLibrary
from aim.osxbuildrules import *


def get_rpath(build: Dict, parsed_toml: Dict):
    # Good blog post about rpath:
    # https://medium.com/@nehckl0/creating-relocatable-linux-executables-by-setting-rpath-with-origin-45de573a2e98
    requires = build.get("requires", [])
    library_paths = []

    for required in requires:
        the_dep = find_build(required, parsed_toml["builds"])
        if the_dep["buildRule"] == "dynamiclib":
            library_paths.append(the_dep["name"])

    build_dir = Path(build["build_dir"]).resolve()
    current_build_dir = build_dir / build["name"]
    library_paths = prepend_paths(build_dir, library_paths)
    relative_paths = [
        relpath(Path(lib_path), current_build_dir) for lib_path in library_paths
    ]

    relative_paths = [f"@executable_path/{rel_path}" for rel_path in relative_paths]
    relative_paths = ["@executable_path"] + relative_paths

    relative_paths_string = escape_path(":".join(relative_paths))
    return f"-rpath '{relative_paths_string}'"


def get_required_library_information(build, parsed_toml):
    requires = build.get("requires", [])
    if not requires:
        return [], [], []

    library_names = []
    library_paths = []
    library_types = []
    for required in requires:
        the_dep = find_build(required, parsed_toml["builds"])
        output_name: str = the_dep["outputName"]
        library_names.append(output_name)
        dep_name = the_dep["name"]
        library_paths.append(dep_name)
        library_types.append(the_dep["buildRule"])

    library_paths = prepend_paths(build["build_dir"], library_paths)
    library_paths = PrefixLibraryPath(library_paths)
    return library_names, PrefixLibrary(library_names), library_paths


class OsxBuilds(GCCBuilds):
    def __init__(self, cxx_compiler, c_compiler, archiver):
        super().__init__(cxx_compiler, c_compiler, archiver)

    def add_rules(self, build):
        directory = build["build_dir"]
        ninja_path = directory / "rules.ninja"
        with ninja_path.open("w+") as ninja_file:
            writer = Writer(ninja_file)
            add_compile(writer)
            add_ar(writer)
            add_exe(writer)
            add_shared(writer)

    def get_required_library_information(self, build, parsed_toml):
        return get_required_library_information(build, parsed_toml)

    def get_rpath(self, build: Dict, parsed_toml: Dict):
        return get_rpath(build, parsed_toml)

    # TODO: These should take version strings as well.
    def add_static_library_naming_convention(self, library_name):
        return f"lib{library_name}.a"

    def add_dynamic_library_naming_convention(self, library_name):
        return f"lib{library_name}.dylib"

    def add_exe_naming_convention(self, exe_name):
        return f"{exe_name}.exe"
