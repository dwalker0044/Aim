import functools
import itertools
import subprocess
import sys
from pathlib import Path
from typing import *

import toml
from schema import target_schema


# Convenient typedefs
#
StringList = List[str]
PathList = List[Path]

# Globals
# CompilerC and CompilerCpp are used everywhere.
# Callables are compiler frontend dependent.
#
CompilerC: str
CompilerCpp: str
Archiver: str
PrefixIncludePath: Callable
PrefixLibraryPath: Callable
PrefixLibrary: Callable
StaticBuildProcess: Callable
DynamicBuildProcess: Callable
ExeBuildProcess: Callable
ToObjectFiles: Callable

# A type variable so function types can vary.
#
T = TypeVar('T')


def run_clean_process(globs: StringList, path: Optional[Path] = None):
    path = Path().cwd() if path is None else Path(path)
    for glob_str in globs:
        for f in path.glob(glob_str):
            print(f"rm {f.name}")
            f.unlink()


def src_to_obj(files) -> StringList:
    return [x.stem + ".obj" for x in files]


def src_to_o(files) -> StringList:
    return [x.stem + ".o" for x in files]


def to_str(paths) -> StringList:
    return [str(x) for x in paths]


def to_paths(string_paths) -> PathList:
    return [Path(x) for x in string_paths]


def glob(glob_string, paths: PathList) -> List[PathList]:
    return [list(x.glob(glob_string)) for x in paths]


def flatten(list_of_lists: List[List[T]]) -> List[T]:
    return list(itertools.chain.from_iterable(list_of_lists))


def prefix(the_prefix, paths) -> StringList:
    return [the_prefix + str(x) for x in paths]


def suffix(the_suffix, paths) -> StringList:
    return [str(x) + the_suffix for x in paths]


def gcc_static_build_process(cxxflags: StringList, files: PathList, defines: Optional[str] = None,
                             includes: Optional[Path] = None):
    includes = [] if includes is None else includes
    defines = [] if defines is None else defines

    print("Building static library...")
    print(f"CXXFLAGS: {cxxflags}")
    print(f"DEFINES: {defines}")
    print(f"INCLUDE_PATHS: {includes}")
    print("")
    result = subprocess.run(
        [CompilerCpp, "-c"] + cxxflags + defines + includes + to_str(files), capture_output=True)

    if result.returncode != 0:
        print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        print("-----------------")
        print("Build Failed.")
        print("-----------------")
        exit(1)


def msvc_static_build_process(cxxflags: StringList, files: PathList, defines: Optional[str] = None,
                              includes: Optional[Path] = None):
    includes = [] if includes is None else includes
    defines = [] if defines is None else defines

    print("Building static library...")
    print(f"CXXFLAGS: {cxxflags}")
    print(f"DEFINES: {defines}")
    print(f"INCLUDE_PATHS: {includes}")
    print("")
    result = subprocess.run(
        [CompilerCpp, "/c"] + cxxflags + defines + includes + to_str(files), capture_output=True)

    if result.returncode != 0:
        print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        print("-----------------")
        print("Build Failed.")
        print("-----------------")
        exit(1)


def run_ar_process(libname: str, files: StringList):
    print("Archiving...")
    print(f"LIB_NAME {libname}")
    print("")
    result = subprocess.run([Archiver, "-r", libname] + files, capture_output=True)

    if result.returncode != 0:
        print(result)
        print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        print("-----------------")
        print("Build Failed.")
        print("-----------------")
        exit(1)


def build_static_library(build, cxxflags: Optional[StringList] = None, defines: Optional[StringList] = None):
    cxxflags = [] if cxxflags is None else cxxflags
    defines = [] if defines is None else defines

    # Remember, this is the output name, not the linker arguments.
    library_name = build["outputName"]

    include_paths = PrefixIncludePath(to_paths(build["includePaths"]))
    src_paths = build["srcDirs"]
    src_files = flatten(glob("*.cpp", to_paths(src_paths)))
    objs = ToObjectFiles(src_files)

    StaticBuildProcess(cxxflags, src_files, defines, include_paths)
    run_ar_process(library_name, objs)


def gcc_build_executable(build: Dict, cxxflags: Optional[StringList] = None, defines: Optional[StringList] = None):
    cxxflags = [] if cxxflags is None else cxxflags
    defines = [] if defines is None else defines

    src_paths = build["srcDirs"]
    src_files = to_str(flatten(glob("*.cpp", to_paths(src_paths))))

    exe_name = build["outputName"]
    includes = PrefixIncludePath(to_paths(build["includePaths"]))
    library_paths = PrefixLibraryPath(to_paths(build["libraryPaths"]))
    libraries = PrefixLibrary(build["libraries"])

    linker_args = library_paths + libraries

    print("Building executable...")
    print(f"CXXFLAGS: {cxxflags}")
    print(f"DEFINES: {defines}")
    print(f"INCLUDE_PATHS: {includes}")
    print(f"LIBRARY_PATHS: {library_paths}")
    print(f"LIBRARIES: {libraries}")
    print("")
    result = subprocess.run(
        [CompilerCpp] + cxxflags + defines + includes + src_files + ["-o", exe_name] + linker_args,
        capture_output=True)

    if result.returncode != 0:
        print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        print("-----------------")
        print("Build Failed.")
        print("-----------------")
        exit(1)


def msvc_build_executable(build: Dict, cxxflags: Optional[StringList] = None, defines: Optional[StringList] = None):
    cxxflags = [] if cxxflags is None else cxxflags
    defines = [] if defines is None else defines

    src_paths = build["srcDirs"]
    src_files = to_str(flatten(glob("*.cpp", to_paths(src_paths))))

    exe_name = build["outputName"]
    includes = PrefixIncludePath(to_paths(build["includePaths"]))
    library_paths = PrefixLibraryPath(to_paths(build["libraryPaths"]))
    libraries = PrefixLibrary(build["libraries"])

    linker_args = library_paths + libraries

    print("Building executable...")
    print(f"CXXFLAGS: {cxxflags}")
    print(f"DEFINES: {defines}")
    print(f"INCLUDE_PATHS: {includes}")
    print(f"LIBRARY_PATHS: {library_paths}")
    print(f"LIBRARIES: {libraries}")
    print("")
    result = subprocess.run(
        [CompilerCpp] + cxxflags + defines + includes + src_files + ["/link", "/out:" + exe_name] + linker_args,
        capture_output=True)

    if result.returncode != 0:
        print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        print("-----------------")
        print("Build Failed.")
        print("-----------------")
        exit(1)


def gcc_build_dynamic_library(build: Dict, cxxflags: Optional[StringList] = None, defines: Optional[StringList] = None):
    cxxflags = [] if cxxflags is None else cxxflags
    defines = [] if defines is None else defines

    includes = build["includePaths"]
    src_paths = build["srcDirs"]
    src_files = to_str(flatten(glob("*.cpp", to_paths(src_paths))))

    lib_name = build["outputName"]
    library_paths = PrefixLibraryPath(to_paths(["libraryPaths"]))
    libraries = PrefixLibrary(build["libraries"])

    linker_args = library_paths + libraries

    print("Building dynamic library...")
    print(f"CXXFLAGS: {cxxflags}")
    print(f"DEFINES: {defines}")
    print(f"INCLUDE_PATHS: {includes}")
    print(f"LIBRARY_PATHS: {library_paths}")
    print(f"LIBRARIES: {libraries}")
    result = subprocess.run(
        ["clang-cl"] + cxxflags + defines + includes + src_files + ["-o" + lib_name] + linker_args,
        capture_output=True)

    if result.returncode != 0:
        print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        print("-----------------")
        print("Build Failed.")
        print("-----------------")
        exit(1)


def msvc_build_dynamic_library(build: Dict, cxxflags: Optional[StringList] = None,
                               defines: Optional[StringList] = None):
    cxxflags = [] if cxxflags is None else cxxflags
    defines = [] if defines is None else defines

    includes = build["includePaths"]
    src_paths = build["srcDirs"]
    src_files = to_str(flatten(glob("*.cpp", to_paths(src_paths))))

    lib_name = build["outputName"]
    library_paths = PrefixLibraryPath(to_paths(["libraryPaths"]))
    libraries = PrefixLibrary(build["libraries"])

    linker_args = library_paths + libraries

    print("Building dynamic library...")
    print(f"CXXFLAGS: {cxxflags}")
    print(f"DEFINES: {defines}")
    print(f"INCLUDE_PATHS: {includes}")
    print(f"LIBRARY_PATHS: {library_paths}")
    print(f"LIBRARIES: {libraries}")
    result = subprocess.run(
        ["clang-cl"] + cxxflags + defines + includes + src_files + ["/link", "/DLL", "/out:" + lib_name] + linker_args,
        capture_output=True)

    if result.returncode != 0:
        print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        print("-----------------")
        print("Build Failed.")
        print("-----------------")
        exit(1)




def parse_toml_file(build_name: str):
    global CompilerC, CompilerCpp, Archiver, PrefixIncludePath, PrefixLibraryPath, PrefixLibrary, StaticBuildProcess, \
        DynamicBuildProcess, ExeBuildProcess, ToObjectFiles

    if build_name == "clean":
        run_clean_process(["*.lib", "*.o", "*.obj", "*.pdb", "*.ilk", "*.exe"])
        return

    # TODO: Should we always clean the project?
    run_clean_process(["*.lib", "*.o", "*.obj", "*.pdb", "*.ilk", "*.exe"])

    fd = open("target.toml", "r")
    parsed_toml = toml.loads(fd.read())
    target_schema(parsed_toml)

    CompilerC = parsed_toml["cxx"]
    CompilerCpp = parsed_toml["cc"]
    Archiver = parsed_toml["ar"]

    frontend = parsed_toml["compilerFrontend"]

    if frontend == "msvc":
        PrefixIncludePath = functools.partial(prefix, "/I")
        PrefixLibraryPath = functools.partial(prefix, "/LIBPATH:")
        PrefixLibrary = functools.partial(prefix, "")
        StaticBuildProcess = msvc_static_build_process
        DynamicBuildProcess = msvc_build_dynamic_library
        ExeBuildProcess = msvc_build_executable
        ToObjectFiles = src_to_obj
    else:
        PrefixIncludePath = functools.partial(prefix, "-I")
        PrefixLibraryPath = functools.partial(prefix, "-L")
        PrefixLibrary = functools.partial(prefix, "-l")
        StaticBuildProcess = gcc_static_build_process
        DynamicBuildProcess = gcc_build_dynamic_library
        ExeBuildProcess = gcc_build_executable
        ToObjectFiles = src_to_o

    flags = parsed_toml["flags"]
    defines = parsed_toml["defines"]

    builds = parsed_toml["builds"]

    # TODO: handle build names that don't exist in the toml file.
    # TODO: ensure build names are unique.
    def find_build(_name):
        for build in builds:
            if build["name"] == _name:
                return build
        else:
            raise RuntimeError(f"Failed to find build with name: {build_name}")

    the_build = find_build(build_name)

    # Remember, dependencies are build in the order specified. Might need to
    # update this in the future if we ever to more complex dependency resolution.
    requires = the_build["requires"]
    for dependency in requires:
        dep_build = find_build(dependency)
        run_build_rule(dep_build, flags, defines)

    run_build_rule(the_build, flags, defines)


def run_build_rule(build: Dict, flags: StringList, defines: StringList):
    if build["buildRule"] == "staticlib":
        build_static_library(build, flags, defines)
    elif build["buildRule"] == "exe":
        ExeBuildProcess(build, flags, defines)
    elif build["buildRule"] == "dynamiclib":
        DynamicBuildProcess(build, flags, defines)


def exec():
    build_arg = sys.argv[1]
    parse_toml_file(build_arg)
