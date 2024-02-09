# Doublons (1.0.0)

This program finds duplicates files (hash-based) in a directory and removes them.
For example, if you have the following files:

- test.txt
- test - Copie.txt
- test (2).txt

The program will remove the last two files if they have the same content as the first one.

It will also change the name of the files to remove the suffixes, for example:

- test - Copie.txt -> test.txt
- test (2).txt -> test.txt

Even if the files don't have duplicates.

# Usage

To run doublons in a specific directory from the installed poetry environment:

```bash
poetry run doublons <directory>
```

There are instructions for how to install `doublons` in such an environment below.
Try `poetry run doublons --help` for a list of all possible options.

# Installation

I recommend using `pipx` to install `poetry` in an isolated environment, then using `poetry` to manage the program dependencies.

On `Linux`, one way to install `pipx` is:

```bash
python3 -m pip install --user pipx # On Windows you may need to replace all occurences of 'python3' by 'py'
python3 -m pipx ensurepath
```

You can restart your terminal, then you can install poetry:

```bash
pipx install poetry
```

At which point you can install the dependencies:

```bash
git clone https://github.com/JonathanCabezas/doublons.git
cd doublons
poetry install
```

# Build

I like to use `nuitka` to have a single `.exe` file I can send to non-tech-savvy friends.
There is an example to compile to a single `.exe` file on `Windows` in the `build.sh` script.

# Changelog (placeholder)

## x.x.x - 202x-month-day

### Fixed

- placeholder

### Changed

- placeholder

### Added

- placeholder

# TODOS

- Check why version doesn't return the version from the `pyproject.toml`
- Added a log file
