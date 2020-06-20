import functools

from ninja_syntax import Writer

from aim.gccbuildrules import *
from aim.utils import *

PrefixIncludePath = functools.partial(prefix, "-I")
PrefixLibraryPath = functools.partial(prefix, "-L")
PrefixLibrary = functools.partial(prefix, "-l:")
ToObjectFiles = src_to_o


def get_src_files(build):
    directory = build["directory"]
    src_dirs = build["srcDirs"]
    src_paths = append_paths(directory, src_dirs)
    src_files = flatten(glob("*.cpp", src_paths))
    assert src_files, f"Fail to find any source files in {to_str(src_paths)}."
    return src_files


def get_include_paths(build):
    directory = build["directory"]
    include_paths = build.get("includePaths", [])
    includes = append_paths(directory, include_paths)
    includes = PrefixIncludePath(includes)
    return includes


def get_library_paths(build):
    directory = build["directory"]
    library_paths = build.get("libraryPaths", [])
    library_paths = append_paths(directory, library_paths)
    library_paths = PrefixLibraryPath(library_paths)
    return library_paths


def get_library_information(build):
    libraries = build.get("libraries", [])
    link_libraries = PrefixLibrary(libraries)
    return libraries, link_libraries


def get_third_party_library_information(build):
    third_libraries = build.get("thirdPartyLibraries", [])
    third_libraries = PrefixLibrary(third_libraries)
    return third_libraries


class GCCBuilds:
    def __init__(self, cxx_compiler, c_compiler, archiver):
        self.cxx_compiler = cxx_compiler
        self.c_compiler = c_compiler
        self.archiver = archiver

    def add_rules(self, build):
        directory = build["directory"]
        ninja_path = directory / "rules.ninja"
        with ninja_path.open("w+") as ninja_file:
            writer = Writer(ninja_file)
            add_compile(writer)
            add_ar(writer)
            add_exe(writer)
            add_shared(writer)

    def build(self, build):
        the_build = build["buildRule"]

        build_name = build["name"]
        project_dir = build["directory"]

        build_path = project_dir / build_name
        build_path.mkdir(parents=True, exist_ok=True)

        ninja_path = build_path / "build.ninja"
        build["buildPath"] = build_path

        self.add_rules(build)

        with ninja_path.open("w+") as ninja_file:
            ninja_writer = Writer(ninja_file)
            rule_path = (project_dir / "rules.ninja").resolve()
            ninja_writer.include(escape_path(str(rule_path)))
            ninja_writer.newline()

            if the_build == "staticlib":
                self.build_static_library(ninja_writer, build)
            elif the_build == "exe":
                self.build_executable(ninja_writer, build)
            elif the_build == "dynamiclib":
                self.build_dynamic_library(ninja_writer, build)
            else:
                raise RuntimeError(f"Unknown build type {the_build}.")

    def add_compile_rule(self, nfw: Writer, build: Dict):
        cxxflags = build["flags"]
        defines = build["defines"]

        src_files = get_src_files(build)
        includes = get_include_paths(build)

        # Its very important to specify the absolute path to the obj files.
        # This prevents recompilation of files when an exe links against a library.
        # Without the absolute path to the obj files, it would build the files again
        # in the current (exe's) build location.
        build_path = build["buildPath"]
        obj_files = ToObjectFiles(src_files)
        obj_files = append_paths(build_path, obj_files)

        file_pairs = zip(to_str(src_files), to_str(obj_files))
        for src_file, obj_file in file_pairs:
            nfw.build(outputs=obj_file,
                      rule="compile",
                      inputs=src_file,
                      variables={
                          "compiler": self.cxx_compiler,
                          "includes": includes,
                          "flags": cxxflags,
                          "defines": defines
                      })
            nfw.newline()

        return obj_files

    def build_static_library(self, nfw: Writer, build: Dict):
        build_name = build["name"]
        library_name = build["outputName"]

        obj_files = self.add_compile_rule(nfw, build)

        nfw.build(outputs=library_name,
                  rule="ar",
                  inputs=to_str(obj_files))
        nfw.newline()

        nfw.build(rule="phony",
                  inputs=library_name,
                  outputs=build_name)
        nfw.newline()

    def build_executable(self, nfw, build: Dict):
        build_name = build["name"]
        exe_name = build["outputName"]
        cxxflags = build["flags"]
        defines = build["defines"]
        requires = build.get("requires", [])
        build_path = build["buildPath"]

        includes = get_include_paths(build)
        library_paths = get_library_paths(build)
        libraries, link_libraries = get_library_information(build)
        third_libraries = get_third_party_library_information(build)

        linker_args = library_paths + link_libraries + third_libraries

        for requirement in requires:
            ninja_file = (build_path.parent / requirement / "build.ninja").resolve()
            assert ninja_file.exists(), f"Failed to find {str(ninja_file)}."
            nfw.subninja(escape_path(str(ninja_file)))
            nfw.newline()

        obj_files = self.add_compile_rule(nfw, build)

        nfw.build(outputs=exe_name,
                  rule="exe",
                  inputs=to_str(obj_files),
                  implicit=libraries,
                  variables={
                      "compiler": self.cxx_compiler,
                      "includes": includes,
                      "flags": cxxflags,
                      "defines": defines,
                      "exe_name": exe_name,
                      "linker_args": " ".join(linker_args)
                  })
        nfw.newline()

        nfw.build(rule="phony",
                  inputs=exe_name,
                  outputs=build_name)
        nfw.newline()

    def build_dynamic_library(self, nfw, build: Dict):
        build_name = build["name"]
        lib_name = build["outputName"]
        cxxflags = build["flags"]
        defines = build["defines"]

        includes = get_include_paths(build)
        library_paths = get_library_paths(build)
        libraries, link_libraries = get_library_information(build)
        third_libraries = get_third_party_library_information(build)

        linker_args = library_paths + link_libraries + third_libraries

        obj_files = self.add_compile_rule(nfw, build)

        build_path = build["buildPath"]
        output_name = str(build_path / lib_name)
        nfw.build(rule="shared",
                  inputs=to_str(obj_files),
                  implicit=libraries,
                  outputs=output_name,
                  variables={
                      "compiler": self.cxx_compiler,
                      "includes": includes,
                      "flags": " ".join(cxxflags),
                      "defines": " ".join(defines),
                      "lib_name": lib_name,
                      "linker_args": " ".join(linker_args)
                  })
        nfw.newline()

        nfw.build(rule="phony",
                  inputs=output_name,
                  outputs=lib_name)

        nfw.newline()


def log_build_information(build):
    build_name = build["name"]
    cxxflags = build["flags"]
    defines = build["defines"]
    includes = build["includes"]
    library_paths = build["libraryPaths"]
    output = build["outputName"]

    print(f"Running build: f{build_name}")
    print(f"CXXFLAGS: {cxxflags}")
    print(f"DEFINES: {defines}")
    print(f"INCLUDE_PATHS: {includes}")
    print(f"LIBRARY_PATHS: {library_paths}")
    print(f"OUTPUT NAME: {output}")
    print("")
