# Aim
Aim is a command line tool for building C++ projects from Target files. 
A Target file is written in TOML.

Aim doesn't try to be too clever. It simply generates the compiler arguments
from the Target file and runs the command in a subprocess.

## Getting Started
### Prerequisites
* Python 3.7

### Installing
Clone the project.

Then install Aim:
```
python setup.py install
```

Or if you are a developer:
```
python setup.py develop
```

### Example
Create a project structure:
```
Project
-- builds
  -- windows-clang_cl-debug
    -- target.toml
-- demo
  -- main.cpp
```
Where the directories inside build should be for each target you want to compile for. For now we have one target `windows-clang_cl-debug`, which indicates
that the target is for the `Windows` operating system, using the `clang-cl` compiler and is a `debug` build.

Examples of other targets could be:
* windows-clang\_cl-release
* debian-clang-debug
* ubuntu-clang-asan


Fill out the `target.toml` file:
```toml
cxx = "clang-cl"
cc = "clang-cl"
ar = "llvm-ar"
compilerFrontend="msvc"

flags = [
    "/std:c++17",
    "/Zi",
]

defines = []

[[Builds]]
    name = "demo"
    buildRule = "exe"
    requires = []
    outputName = "Demo.exe"
    srcDirs = ["../../demo"]
    includePaths = []
    libraryPaths = []
    libraries = []
```

Write hello world in `main.cpp`.

And then build the project:
```
aim demo
```

## Philosophies
Building C++ is hard. Managing dependencies is also hard. 
Rather then over complicate things, Aim will take the compiler 
arguments described in the target file and will build the project 
using those arguments. 
Aim does a little bit of work for the developer:
* Provides the `compile only` flag when building static libraries.
* Manages include and library path arguments.
* Manages the arguments when linking against 3rd party libraries 
* Handles the some additional linker flags when building with msvc.

And that's it. The rest is up to you.
