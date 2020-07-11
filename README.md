<p align="center">
<img src="https://github.com/diwalkerdev/Assets/blob/master/Aim/aim.png" width="300" height="300">
</p>

# Aim
Aim is a command line tool for building C++ projects. Its primary goal is to simplify building C++ libraries and executables, for different build targets, whilst being easy to use and fast.

A build target is some combination of _things_ that affects the output binary. This could be some combination of operating system, compiler and build type and maybe more. For example, the build target `linux-clang++-release` indicates that this is a `release` build, using the `clang++` compiler for the `linux` operating system.

Support for a build target is added by writing a `target.toml` file. For more information on the `toml` file format see the [toml github page](https://github.com/toml-lang/toml). 
Each `target.toml` file must be written out in full for each target that you need to support. There is no way for target files to share information or to depend on another. While this leads to duplication between target files, it makes them very explicit and makes debugging builds much easier.

## Known Limitations
* Windows support is still in development.

## Why another build tool?
Aim is an attempt to make building C++ projects as simple as possible. It is very easy to add libraries and other executables to a project. Other build tools seem overly complex and require users to learn new sytaxes. 

With Aim:
* adding build targets is simple and explicit
* all builds occur in their own directory by default
* builds are fast and reliable executed by the `ninja` build system.

All you have to do is write the `target.toml` file. It is very easy.


## Getting Started
### Prerequisites
Aim requires the following dependencies:
* [python](https://www.python.org/) - version 3.7 or above.
* [ninja](https://ninja-build.org/)
* [poetry](https://python-poetry.org/) - for development only

### Installation
Aim is a `python` project and is installed using `pip`.

```
pip install --user aim-build
```

### Using

<img src="https://github.com/diwalkerdev/Assets/blob/master/Aim/aim-init-demo.gif?raw=true" width="600px">

Note, `aim init` has an optional flag `--demo`. This adds some simple source files to the project for demonstration purposes.

There are 3 main commands:
* `list` - Displays the builds for the target
* `init` - Creates a project structure
* `build` - Executes a build

For more information run:
```
aim <command> --help
```

## Developing Aim

Aim is a Python project and uses the [poetry](https://python-poetry.org/) dependency manager. See [poetry installation](https://python-poetry.org/docs/#installation) for instructions.

Once you have cloned the project, the virtual environment and dependencies can be installed simply by executing:

```
poetry install
```

### Dev Install
Unfortunately, unlike `setuptools`, there is no means to do a 'dev install' using poetry. A dev install causes a command line script to use the current development code which is useful so a project does not need to be reinstalled after every modification. 

In order to use Aim on the command line, is it recommended to create an alias. The alias needs to:
* adds Aim to `PYTHONPATH` to resolve import/module paths 
* execute the main Aim script using virtualenv's python

For `bash` this looks like:
```
alias aim="PYTHONPATH=$PWD/src $(poetry env info -p)/bin/python $PWD/src/aim_build/main.py"
```

For `fish` shell this looks like:
```
alias aim="PYTHONPATH=$PWD/src "(poetry env info -p)"/bin/python $PWD/src/aim_build/main.py"
```

## Other remarks
The target file can be extended with other builds. For example to add unit tests. Begin by partitioning any code that
needs to be tested into a library. Then create another build for the test. Since unit tests are really an executable,
set `buildRule="exe"` and add the library to the `requires` list. Remember to update the build for the primary
executable as well if you have one.

The unit tests can now be built and run like any other executable.

## Future improvements / known limitations
 * The `cc` field isn't actually used at the moment. All build steps are performed by the cxx compiler.
