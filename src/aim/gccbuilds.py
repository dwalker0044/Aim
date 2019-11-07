import functools

from ninja_syntax import Writer

from aim.gccbuildrules import GCCBuildRules
from aim.utils import *

PrefixIncludePath = functools.partial(prefix, "-I")
PrefixLibraryPath = functools.partial(prefix, "-L")
PrefixLibrary = functools.partial(prefix, "-l")
ToObjectFiles = src_to_o


class GCCBuilds:
    def __init__(self, nfw: Writer, cxx_compiler, c_compiler, archiver):
        self.nfw = nfw
        self.cxx_compiler = cxx_compiler
        self.c_compiler = c_compiler
        self.archiver = archiver
        self.builder = GCCBuildRules(self.nfw, self.cxx_compiler)

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

        includes = build["includePaths"]
        include_paths = append_paths(directory, includes)
        includes = PrefixIncludePath(include_paths)

        self.builder.add_compile(cxxflags, defines, includes)
        self.builder.add_ar()

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

        includes = getattr(build, "includePaths", [])
        include_paths = append_paths(directory, includes)
        includes = PrefixIncludePath(include_paths)

        library_paths = getattr(build, "libraryPaths", [])
        library_paths = append_paths(directory, library_paths)
        library_paths = PrefixLibraryPath(library_paths)

        libraries = getattr(build, "libraries", [])
        libraries = PrefixLibrary(libraries)

        third_libraries = getattr(build, "thirdPartyLibraries", [])
        third_libraries = PrefixLibrary(third_libraries)

        linker_args = library_paths + libraries + third_libraries

        self.builder.add_exe(exe_name,
                             defines,
                             cxxflags,
                             includes,
                             linker_args)

        self.nfw.build(outputs=exe_name,
                       rule="exe",
                       inputs=to_str(src_files),
                       implicit=libraries)
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

        includes = getattr(build, "includePaths", [])
        include_paths = append_paths(directory, includes)
        includes = PrefixIncludePath(include_paths)

        library_paths = getattr(build, "libraryPaths", [])
        library_paths = append_paths(directory, library_paths)
        library_paths = PrefixLibraryPath(library_paths)

        libraries = getattr(build, "libraries", [])
        libraries = PrefixLibrary(libraries)

        third_libraries = getattr(build, "thirdPartyLibraries", [])
        third_libraries = PrefixLibrary(third_libraries)

        linker_args = library_paths + libraries + third_libraries

        self.builder.add_shared(lib_name,
                                defines,
                                cxxflags,
                                includes,
                                linker_args)
        self.nfw.build(rule="shared",
                       inputs=to_str(src_files),
                       outputs=lib_name,
                       implicit=libraries)
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
