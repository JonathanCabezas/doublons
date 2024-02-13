# Doublons (1.0.2)

This program finds duplicates files (hash-based) in a directory and removes them.
For example, if you have the following files:

- test.txt
- test - Copie.txt
- test (2).txt

The program will remove (move to a `trash` folder to avoid loss of data) the last two files if they have the same content as the first one.

It will also change the name of the files to remove the suffixes, for example:

- test - Copie.txt -> test.txt
- test (2).txt -> test.txt

Even if the files don't have duplicates.

# Usage

To run doublons in a specific directory from the installed poetry environment:

```bash
poetry run doublons.py <directory>
```

There are instructions for how to install `doublons` in such an environment below.
Try `poetry run doublons --help` for a list of all possible options.

`Doublons` will run on files which match the pattern in the `whitelist` file and don't match the pattern in the `blacklist` file.

# Whitelist/Blacklist syntax

The syntax is based on the `.gitignore` format, with only 2 special characters implemented:

- The `*` character means anything that is not a slash
- The `**` can be any number of directories (even 0)

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

# Changelog

## 1.0.2 - 2024-02-13

### Added

- Added a whitelist along with the blacklist for more control of which files are handled

### Changed

- Now using the library `Mio` to produce output and logs (which correctly logs tracebacks on Exceptions)

## 1.0.1 - 2024-02-09

### Added

- Logs in `doublons.log`

# TODOS

- Logs may no be perfect as they don't includes `input` prints and `user` input
- It could be nice to undo the work of the program
