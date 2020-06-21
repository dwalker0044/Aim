# Aim
Aim is a command line tool for building C++ projects.
Each build target has it's own Target file.
A build target could be Windows or Linux and variations of the build such as Debug and Release.
A Target file is written in TOML.

Aim doesn't try to be too clever. For each target the Target file must be written out in full. Aim doesn't attempt
to do any auto-detection or automatic resolution of variables. What you see is what you get. While the duplication may
be a bit annoying, build errors are far easier to debug.

## Limitations
* Supports only Linux.
* Some Windows support via LLVM but hasn't been tested for a while.

## Why another build tool?
Other build tools are far too difficult to use. Aim allows you to partition a project into a executables, static libraries
and shared libraries for any number of different build targets (Debug, Release, Sanitized). All builds occur in their own
directory and dependency tracking is managed by Ninja.

All you have to do is write the target file in TOML. It is stupidly easy. No weird new syntax that you'll probably
use nowhere else.

## Getting Started
Aim is a python project. It uses [poetry](https://python-poetry.org/) for the project and dependency manager.
Installation must be done using `poetry`.

### Prerequisites
* Python 3.7 or above.
* [poetry](https://python-poetry.org/)

### Installing
Clone the project.

Then install Aim using Poetry

`poetry install`

Check aim has been installed:

`aim --help`

### Using
Create a folder for your project `AimDemoProject` and `cd` into it.

Now initialise the directory:

`aim init`

The following output will be displayed:

```
Creating directories...
	/home/username/AimDemoProject/headers
	/home/username/AimDemoProject/src
	/home/username/AimDemoProject/lib
	/home/username/AimDemoProject/builds
Creating common build targets...
	/home/username/AimDemoProject/builds/windows-clang_cl-debug
		/home/username/AimDemoProject/builds/windows-clang_cl-debug/target.toml
	/home/username/AimDemoProject/builds/windows-clang_cl-release
		/home/username/AimDemoProject/builds/windows-clang_cl-release/target.toml
	/home/username/AimDemoProject/builds/linux-clang++-debug
		/home/username/AimDemoProject/builds/linux-clang++-debug/target.toml
	/home/username/AimDemoProject/builds/linux-clang++-release
		/home/username/AimDemoProject/builds/linux-clang++-release/target.toml
```

Aim has created some folders for you. Don't feel like you have to use this structure.
The important directory is the `build` directory. Aim has assumed that you want to target `Windows` and `Linux`
and that you'll need a `debug` and `release` build for each. Each target is made up of the the platform (Linux/Window),
the compiler (linux-clang++/clang_cl) and the build mode (debug/release). Each target has it's own `target.toml` file.

Let's take a look at the `linux-clang++-debug/target.toml` file:

```toml
cxx = "clang++"                         # the cxx compiler to use.
cc = "clang"                            # the cc compiler to use.
ar = "llvm-ar"                          # the archiver to use.
compilerFrontend="gcc"                  # informs aim of which additional flags to include at various stages of the build.

flags = [                               # compiler flags pass to all build targets.
    "-std=c++17",
    "-g"
]

defines = []                            # defines passed to all build targets.

[[builds]]                              # a list of builds.
    name = "lib_calculator"             # the unique name for this build.
    buildRule = "staticlib"             # the type of build, in this case create a static library.
    outputName = "libCalculator.a"      # the library output name,
    srcDirs = ["../../lib"]             # the src directories  to build the static library from.
    includePaths = ["../../includes"]   # additional include paths to use during the build.

#[[builds]]
#    name = "lib_calculator_so"         # the unique name for this build.
#    buildRule = "dynamiclib"           # the type of build, in this case create a shared library.
#    outputName = "libCalculator.so"    # the library output name,
#    srcDirs = ["../../lib"]            # the src directories to build the shared library from.
#    includePaths = ["../../includes"]  # additional include paths to use during the build.

[[builds]]
    name = "exe"                        # the unique name for this build.
    buildRule = "exe"                   # the type of build, in this case an executable.
    requires = ["lib_calculator"]       # a build dependency. "shared" will be built first and linked against.
    outputName = "the_calculator.exe"   # the exe output name,
    srcDirs = ["../../src"]             # the src directories to build the shared library from.
    includePaths = ["../../includes"]   # additional include paths to use during the build.
    libraryPaths = ["./lib_calculator"] # you must manually specify the library path to the dependency (requires).
    libraries = ["libCalculator.a"]    # you must manually specify the library name of the dependency (requires).
    #thirdPartyLibraries = []           # additional libraries to use during the build that are not apart of the Aim build process.
```
For the complete set of options, please refer to `src/aim/schema.py`.
For the full set of the automatic option that Aim adds to build steps, see `gccbuildrules.py` or `msvcbuildrules.py`.
All paths a relative to the target build directory hence why things like the `srcDirs` are prefixed with `../../`.

By default `init` adds a very simple `main.cpp` and calculator library library to the project. By default the library
is created as a static library. You can change this to a dynamic library by uncommenting the `lib_calculator_so` build
and updating the `requires`, `libraryPaths` and `library` fields in the `exe` build.

Build the project:
`aim build --target exe --path builds/linux-clang++-debug/`

Note if you build using the dynamic library, the shared object needs to be copied to the executable directory before the
exe will run. Otherwise you'll get a "shared object not found error."

### Other remarks
The target file can be extended with other builds. For example to add unit tests, partition any code that needs to be
tested into a library. Then create another build with `buildRule="exe"` and add the library to the `requires` list.
Remember to do this for your executable as well if you have one. The unit tests can now be build like any other build.

### Future improvements / known limitations
 * The fields `libraryPaths` and `libraries` should be resolved automatically from the `requires` entry.
 * The `cc` field isn't actually used at the moment. All build steps are performed by the cxx compiler.
 * Automatic redistribution of outputs. Currently dynamic libraries need to be manually copied to the executables directory before it will run.
