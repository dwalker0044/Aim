import functools

from ninja_syntax import Writer

from aim.msvcbuildrules import WindowsBuildRules
from aim.utils import *

PrefixIncludePath = functools.partial(prefix, "/I")
PrefixLibraryPath = functools.partial(prefix, "/LIBPATH:")
PrefixLibrary = functools.partial(prefix, "")
ToObjectFiles = src_to_obj


def implicit_library_inputs(libraries):
    implicits = []
    for library in libraries:
        parts = library.split(".")
        if parts[1] == "dll":
            implicits.append(parts[0] + ".exp")
            implicits.append(parts[0] + ".lib")
        implicits.append(library)

    return implicits


def convert_dlls_to_lib(libraries):
    new_libraries = []
    for library in libraries:
        parts = library.split(".")
        if parts[1] == "dll":
            new_libraries.append(parts[0] + ".lib")
        else:
            new_libraries.append(library)

    return new_libraries


class MSVCBuilds:
    def __init__(self, nfw: Writer, cxx_compiler, c_compiler, archiver):
        self.nfw = nfw
        self.cxx_compiler = cxx_compiler
        self.c_compiler = c_compiler
        self.archiver = archiver

    def build(self, build):
        the_build = build["buildRule"]
        if the_build == "staticlib":
            self.build_static_library(build)
        elif the_build == "exe":
            self.build_executable(build)
        elif the_build == "dynamiclib":
            self.build_dynamic_library(build)
        else:
            raise RuntimeError(f"Unknown build type {the_build}.")

    def build_static_library(self, build: Dict):
        build_name = build["name"]
        cxxflags = build["flags"]
        defines = build["defines"]
        directory = build["directory"]
        library_name = build["outputName"]

        src_dirs = build["srcDirs"]
        src_paths = append_paths(directory, src_dirs)
        src_files = flatten(glob("*.cpp", src_paths))
        assert src_files, "Fail to find any source files."
        obj_files = ToObjectFiles(src_files)

        include_paths = build.get("includePaths", [])
        include_paths = append_paths(directory, include_paths)
        includes = PrefixIncludePath(include_paths)

        builder = WindowsBuildRules(self.nfw, self.cxx_compiler)
        builder.add_compile(cxxflags, defines, includes)
        builder.add_ar()

        self.nfw.build(outputs=[],
                       implicit_outputs=obj_files,
                       rule="compile",
                       inputs=to_str(src_files))
        self.nfw.newline()

        self.nfw.build(outputs=library_name,
                       rule="ar",
                       inputs=to_str(obj_files))
        self.nfw.newline()

        self.nfw.build(rule="phony",
                       inputs=library_name,
                       outputs=build_name)
        self.nfw.newline()

        print("Static library build information...")
        print(f"LIBNAME: {library_name}")
        print(f"CXXFLAGS: {cxxflags}")
        print(f"DEFINES: {defines}")
        print(f"INCLUDE_PATHS: {includes}")
        print(f"FILES: {to_str(src_files)}")
        print("")

    def build_executable(self, build: Dict):
        build_name = build["name"]
        exe_name = build["outputName"]
        cxxflags = build["flags"]
        defines = build["defines"]
        directory = build["directory"]

        src_dirs = build["srcDirs"]
        src_paths = append_paths(directory, src_dirs)
        src_files = flatten(glob("*.cpp", src_paths))
        assert src_files, "Fail to find any source files."

        include_paths = build.get("includePaths", [])
        include_paths = append_paths(directory, include_paths)
        includes = PrefixIncludePath(include_paths)

        library_paths = build.get("libraryPaths", [])
        library_paths = append_paths(directory, library_paths)
        library_paths = PrefixLibraryPath(library_paths)

        libraries = build.get("libraries", [])
        implicits = implicit_library_inputs(libraries)
        link_libraries = PrefixLibrary(convert_dlls_to_lib(libraries))

        third_libraries = getattr(build, "thirdPartyLibraries", [])
        third_libraries = PrefixLibrary(convert_dlls_to_lib(third_libraries))

        linker_args = library_paths + link_libraries + third_libraries

        builder = WindowsBuildRules(self.nfw, self.cxx_compiler)
        builder.add_exe(exe_name,
                        defines,
                        cxxflags,
                        includes,
                        linker_args)

        self.nfw.build(outputs=exe_name,
                       rule="exe",
                       inputs=to_str(src_files),
                       implicit=implicits)
        self.nfw.newline()

        self.nfw.build(rule="phony",
                       inputs=exe_name,
                       outputs=build_name)
        self.nfw.newline()

        print("Building executable...")
        print(f"CXXFLAGS: {cxxflags}")
        print(f"DEFINES: {defines}")
        print(f"INCLUDE_PATHS: {includes}")
        print(f"LIBRARY_PATHS: {library_paths}")
        print(f"LIBRARIES: {libraries}")
        print("")

    def build_dynamic_library(self, build: Dict):
        build_name = build["name"]
        lib_name = build["outputName"]
        cxxflags = build["flags"]
        defines = build["defines"]
        directory = build["directory"]

        src_dirs = build["srcDirs"]
        src_paths = append_paths(directory, src_dirs)
        src_files = flatten(glob("*.cpp", src_paths))
        assert src_files, "Fail to find any source files."

        include_paths = build.get("includePaths", [])
        include_paths = append_paths(directory, include_paths)
        includes = PrefixIncludePath(include_paths)

        library_paths = build.get("libraryPaths", [])
        library_paths = append_paths(directory, library_paths)
        library_paths = PrefixLibraryPath(library_paths)

        libraries = build.get("libraries", [])
        implicits = implicit_library_inputs(libraries)
        link_libraries = PrefixLibrary(convert_dlls_to_lib(libraries))

        third_libraries = getattr(build, "thirdPartyLibraries", [])
        third_libraries = PrefixLibrary(convert_dlls_to_lib(third_libraries))

        linker_args = library_paths + link_libraries + third_libraries

        builder = WindowsBuildRules(self.nfw, self.cxx_compiler)
        builder.add_shared(lib_name,
                           defines,
                           cxxflags,
                           includes,
                           linker_args)

        name = lib_name.split(".")[0]
        implicit_outputs = [
            name + ".lib",
            name + ".exp"
        ]

        self.nfw.build(rule="shared",
                       inputs=to_str(src_files),
                       outputs=lib_name,
                       implicit=implicits,
                       implicit_outputs=implicit_outputs)
        self.nfw.newline()

        self.nfw.build(rule="phony",
                       inputs=lib_name,
                       outputs=build_name)
        self.nfw.newline()

        print("Building dynamic library...")
        print(f"CXXFLAGS: {cxxflags}")
        print(f"DEFINES: {defines}")
        print(f"INCLUDE_PATHS: {includes}")
        print(f"LIBRARY_PATHS: {library_paths}")
        print(f"LIBRARIES: {libraries}")
        print("")
