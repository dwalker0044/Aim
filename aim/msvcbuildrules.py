from ninja_syntax import Writer

from typedefs import StringList


class WindowsBuildRules:
    def __init__(self, nfw: Writer, compiler: str):
        self.nfw = nfw
        self.compiler = compiler

    def add_compile(self,
                    flags: StringList,
                    defines: StringList,
                    includes: StringList):
        flags = " ".join(flags)
        defines = " ".join(defines)
        includes = " ".join(includes)

        command = f"{self.compiler} {defines} {includes} /showIncludes {flags} -c $in"
        self.nfw.rule(name="compile",
                      description='Compile source files to object files',
                      deps="msvc",
                      command=command)
        self.nfw.newline()

    def add_ar(self):
        self.nfw.rule(name="ar",
                      description='Combine object files into an archive',
                      command="llvm-ar cr $out $in")
        self.nfw.newline()

    def add_exe(self,
                exe_name: str,
                defines: StringList,
                flags: StringList,
                includes: StringList,
                linker_args: StringList):
        flags = " ".join(flags)
        defines = " ".join(defines)
        includes = " ".join(includes)
        linker_args = " ".join(linker_args)

        command = f"{self.compiler} {defines} {flags} {includes} $in /link /out:{exe_name} {linker_args}"
        self.nfw.rule(name="exe",
                      description="Build an executable.",
                      command=command)
        self.nfw.newline()

    def add_shared(self,
                   lib_name: str,
                   defines: StringList,
                   flags: StringList,
                   includes: StringList,
                   linker_args: StringList):
        flags = " ".join(flags)
        defines = " ".join(defines)
        includes = " ".join(includes)
        linker_args = " ".join(linker_args)

        command = f"{self.compiler} {defines} {flags} {includes} $in /link /DLL /out:{lib_name} {linker_args}"
        self.nfw.rule(name="shared",
                      description="Build an shared library.",
                      command=command)
        self.nfw.newline()
