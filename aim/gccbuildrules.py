from ninja_syntax import Writer

from typedefs import StringList


class GCCBuildRules:
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

        command = f"{self.compiler} {flags} -MMD -MF deps.d -c {defines} {includes} $in"
        self.nfw.rule(name="compile",
                      description='Compiles source files into object files',
                      deps="gcc",
                      depfile="deps.d",
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

        command = f"{self.compiler} {defines} {flags} {includes} $in -o {exe_name} {linker_args}"
        self.nfw.rule(name="exe",
                      description="Builds an executable.",
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

        command = f"{self.compiler} {defines} -fPIC -shared -fvisibility=hidden {flags} {includes} $in -o {lib_name} {linker_args}"
        self.nfw.rule(name="shared",
                      description="Builds a shared library.",
                      command=command)
        self.nfw.newline()
