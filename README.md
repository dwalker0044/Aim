<p align="center">
<img src="https://github.com/diwalkerdev/Assets/blob/master/Aim/aim.png" width="300" height="300">
</p>

# Aim

Aim is a command line tool for building C++ projects.

Aim attempts to make building C++ projects, for different targets, as simple as possible.
A build target is some combination of operating system, compiler and build type (and possibly other things). For example `linux-clang++-release`.

Support for a build target is added by writing a target file in TOML format. 
Each build target has its own `target.toml` file and must be written out in full for each target that you need to support.
While the duplication may be a bit annoying, build errors are far easier to debug.

Aim doesn't try to be too clever although it does add a few compiler flags to make building and using libraries simpler.

## Limitations
* Currently only supports Linux.
* Some Windows support via LLVM but hasn't been tested for a while.

## Why another build tool?
Other build tools are far too difficult to use. Aim allows you to partition a project into a executables, static libraries
and shared libraries for any number of different build targets (Debug, Release, Sanitized). All builds occur in their own
directory and dependency tracking is managed by Ninja.

All you have to do is write the `target.toml` file. It is very easy. No weird new syntax that you'll probably
use nowhere else.

## Getting Started
Aim is a python project. It uses [poetry](https://python-poetry.org/) for the dependency manager.

Currently there is no installer and so installation must be done using `poetry` (see Installing below).

### Prerequisites
* Python 3.7 or above.
* [poetry](https://python-poetry.org/)

### Installing

<img src="https://github.com/diwalkerdev/Assets/blob/master/Aim/aim-installation.gif?raw=true" width="600px">

Clone the project.

Then install the dependencies (this also creates a virtual environment):

```
poetry install
```

Unfortunately, unlike `setuptools` there is no means to do a 'dev install' using poetry. So simplest thing to, in order to use Aim, is to create an alias. The alias adds Aim to `PYTHONPATH` to resolve import/module paths and then uses Python in the virtualenv created by poetry to run Aim.

For `bash`:
```
alias aim="PYTHONPATH=$PWD/src $(poetry env info -p)/bin/python $PWD/src/aim/main.py"
```

For `fish` shell:
```
alias aim="PYTHONPATH=$PWD/src "(poetry env info -p)"/bin/python $PWD/src/aim/main.py"
```

Check the alias works correctly:

```
aim --help
```

You should see something similar to:
```
usage: aim [-h] [-v] {init,build} ...

Aim C++ build tool. For more help run aim <command> --help

positional arguments:
  {init,build}   Commands
    init         Initialise the current directory
    build        The build name

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit

```

### Using

<img src="https://github.com/diwalkerdev/Assets/blob/master/Aim/aim-init-demo.gif?raw=true" width="600px">

Create a folder for your project and `cd` into it. For example: `AimDemoProject`.

Now initialise the directory:

```
mkdir AimDemoProject
cd AimDemoProject
aim init
```

The following output will be displayed:

```
Creating directories...
	/home/username/AimDemoProject/headers
	/home/username/AimDemoProject/src
	/home/username/AimDemoProject/lib
	/home/username/AimDemoProject/builds
Creating common build targets...
	/home/username/AimTest/builds/windows-clang_cl-debug/target.toml
	/home/username/AimTest/builds/windows-clang_cl-release/target.toml
	/home/username/AimTest/builds/linux-clang++-debug/target.toml
	/home/username/AimTest/builds/linux-clang++-release/target.toml
```

Aim has created some folders for your project and some build targets for you. Don't feel like you have to keep to the project structure, you can modify the target files to point to any directory.

Aim has create some common build targets: `Windows` and `Linux` operating systems, using `clang_cl` compiler for Windows and `clang++` for Linux, and `debug` and `release` builds created for each. Simply add/delete target directories as required.

Let's take a look at the `linux-clang++-debug/target.toml` file:

```toml
projectRoot = "../.."                   # the relative path from the target build directory to the project src directory.
cxx = "clang++"                         # the cxx compiler to use.
cc = "clang"                            # the cc compiler to use.
ar = "llvm-ar"                          # the archiver to use.
compilerFrontend="gcc"                  # informs aim_build of which additional flags to include at various stages of the build.

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
    includePaths = ["../../include"]   # additional include paths to use during the build.

#[[builds]]
#    name = "lib_calculator_so"         # the unique name for this build.
#    buildRule = "dynamiclib"           # the type of build, in this case create a shared library.
#    outputName = "libCalculator.so"    # the library output name,
#    srcDirs = ["../../lib"]            # the src directories to build the shared library from.
#    includePaths = ["../../include"]  # additional include paths to use during the build.

[[builds]]
    name = "exe"                        # the unique name for this build.
    buildRule = "exe"                   # the type of build, in this case an executable.
    requires = ["lib_calculator"]       # build dependencies. Aim figures out the linker flags for you.
    outputName = "the_calculator.exe"   # the exe output name,
    srcDirs = ["../../src"]             # the src directories to build the shared library from.
    includePaths = ["../../include"]   # additional include paths to use during the build.
    #libraryPaths = []                   # additional library paths, used for including third party libraries.
    #libraries = []                      # additional libraries, used for including third party libraries.
```
For the complete set of options, please refer to `src/aim/schema.py`.

All paths a relative to the target build directory hence why things like the `srcDirs` need to be prefixed with `../../`. 
This will change in the near future.

`init` adds a very simple `main.cpp` and calculator library library to the project. By default the library
is built as a static library. You can replace the `lib_calculator` build with with the `lib_calculator_so` build if you
want the library to be created as a dynamic library. When using dynamic libraries Aim will update `rpath` to include
any dynamic libraries that an executable uses.

Build and run the project:

```
aim build --target exe --path builds/linux-clang++-debug/
./builds/linux-clang++-debug/exe/the_calculator.exe
```

## Other remarks
The target file can be extended with other builds. For example to add unit tests. Begin by partitioning any code that
needs to be tested into a library. Then create another build for the test. Since unit tests are really an executable,
set `buildRule="exe"` and add the library to the `requires` list. Remember to update the build for the primary
executable as well if you have one.

The unit tests can now be built and run like any other executable.

## Future improvements / known limitations
 * The `cc` field isn't actually used at the moment. All build steps are performed by the cxx compiler.
