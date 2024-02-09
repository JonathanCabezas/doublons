import re
import logging
import hashlib
import argparse
import igittigitt

from sys import exit
from pathlib import Path
from shorten_regex import ShortenRegex

# Parameters
VERSION = "1.0.1"

suffixes = [" - Copie", " \(\d+\)"]
ignore_parser = igittigitt.IgnoreParser()
ignore_parser.parse_rule_file(Path(__file__).parent / Path("ignorelist"))

logger = None


def _print(msg="", *args, **kwargs):
    if logger:
        logger.info(msg)
    print(msg, *args, **kwargs)


def setup_logs():
    global logger
    # Setup the logger
    logging.basicConfig(filename="doublons.log", level=logging.INFO)
    logger = logging.getLogger("doublons")


# A multiple lines string description with an example of the program
description = """This program finds duplicates files in a directory and removes them.
For example, if you have the following files:
- test.txt
- test - Copie.txt
- test (2).txt
The program will remove the last two files if they have the same content as the first one.
It will also change the name of the files to remove the suffixes, for example:
- test - Copie.txt -> test.txt
- test (2).txt -> test.txt
Even if the files don't have duplicates.
"""
parser = argparse.ArgumentParser(
    description=description, formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    "--dry-run", action="store_true", help="List duplicate files without removing them"
)
parser.add_argument(
    "--suffixes",
    nargs="+",
    help="List of suffixes to remove from the files",
    default=suffixes,
)
parser.add_argument(
    "--choose-original-name",
    action="store_true",
    help="Ask the user to choose the original name of the file when there are multiple possible names",
)
parser.add_argument(
    "--no-input-before-exit",
    action="store_true",
    help="Don't wait for the user to press a key before exiting the program",
)
parser.add_argument(
    "--version",
    action="version",
    version=f"%(prog)s {VERSION}",
    help="Show the version",
)

# Positional argument
parser.add_argument(
    "directory", nargs="?", default=".", help="The directory to search for duplicates"
)

# Global variables
shorten_regex = ShortenRegex(suffixes)
hash_to_locations = {}
files_to_handle = None
number_of_duplicates = 0
number_of_files_to_shorten = 0

renamings = {}
deletions = {}


def hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()


def compute_hashes(root, **kwargs):
    global files_to_handle
    files_to_handle = set(
        [f for f in root.glob("**/*") if f.is_file() and not ignore_parser.match(f)]
    )
    n = len(files_to_handle)
    _print(f"    Number of files to handle: {n}")

    for i, f in enumerate(files_to_handle):
        h = hash(f)
        hash_to_locations.setdefault(h, []).append(f)
        _print(f"    ({i+1}/{n}) Hash of {f} is {h}", end="\r")

    _print("\n")


def automatic_choice(posibles_names):
    # If a name starts with "IMG" or "VID", we choose it
    for i, p in enumerate(posibles_names):
        if p.startswith("IMG") or p.startswith("VID"):
            return i

    return 0


def schedule_renaming(location, new_location):
    global renamings
    if new_location.exists() or new_location in renamings:
        _print(
            f"    The file '{new_location}' already exists with different content than '{location}'"
        )
        _print(f"    Keeping the file '{location}'")
        return
    _print(f"    Renaming the file '{location}' -> '{new_location}'")
    renamings[new_location] = location


def ensure(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def schedule_deletion(location):
    global deletions
    new_location = Path("Trash") / location
    _print(f"    Moving the file '{location}' to '{new_location}'")
    deletions[new_location] = location


def handle_duplicates(root, choose_original_name=False, **kwargs):
    global files_to_handle, number_of_duplicates, renamings, deletions

    for hash, locations in hash_to_locations.items():
        # If there are multiple locations for the same hash, we have duplicates
        if len(locations) == 1:
            continue

        _print(f"> Hash {hash} has duplicates:\n")
        number_of_duplicates += len(locations) - 1
        files_to_handle -= set(locations)

        # We shorten the names of the duplicate files to find all the possible original names
        posibles_names = []
        for location in locations:
            name = location.name
            if name in posibles_names:
                continue

            shorter_name = shorten_regex.shorten(name)
            if shorter_name:
                name = shorter_name

            posibles_names.append(name)
        posibles_names = sorted(posibles_names)
        choice = 0

        # If there are multiple possible names, we need to make a choice
        if any(posibles_names[0] != p for p in posibles_names):
            _print(f"  There are multiple posibles_names:")
            for i, p in enumerate(posibles_names):
                _print(f"    {i+1} - {p}")

            if choose_original_name:
                while True:
                    try:
                        choice = input(f"  Please choose the correct one (1):")
                        if choice:
                            choice = int(choice) - 1
                            if choice < 0 or choice >= len(posibles_names):
                                raise ValueError
                        break
                    except:
                        pass
            else:
                choice = automatic_choice(posibles_names)
            _print()

        original = posibles_names[choice]
        _print(f"  Choosing the name '{original}' as the original name\n")

        # We detect files with the same name
        name_to_locations = {}
        for location in locations:
            name = location.name
            if name in name_to_locations:
                _print(
                    f"  The file '{location}' has the same name as '{name_to_locations[name]}'\n"
                )
                # We keep the shortest name
                if location < name_to_locations[name]:
                    schedule_deletion(name_to_locations[name])
                else:
                    schedule_deletion(location)
                    continue

            name_to_locations[name] = location

        # When we have the original name, we check if the file already exists
        if original not in name_to_locations:
            location = name_to_locations.popitem()[1]
            new_location = root / Path(original)
            schedule_renaming(location, new_location)
        else:
            _print(f"    Keeping the file '{name_to_locations[original]}'")
            del name_to_locations[original]

        # Deleting all the other files
        for location in name_to_locations.values():
            schedule_deletion(location)

        _print()


def shorten_names_of_other_files(**kwargs):
    global renamings, number_of_files_to_shorten
    _print("\n> Shortening names of other files...\n")

    for f in files_to_handle:
        shorter_name = shorten_regex.shorten(f.name)

        if shorter_name:
            number_of_files_to_shorten += 1
            schedule_renaming(f, f.with_name(shorter_name))


def summarize(**kwargs):
    _print(f"\n> Summary:\n")
    _print(f"    Number of duplicates: {number_of_duplicates}")
    _print(f"    Number of files to shorten: {number_of_files_to_shorten}")
    _print(f"    Number of files to delete: {len(deletions)}")
    _print(f"    Number of files to rename: {len(renamings)}")


def apply_changes(dry_run=False, confirm=True, **kwargs):
    if dry_run:
        return

    choice = "yes"
    while True and confirm:
        _print("\nAre you sure you want to continue (yes/NO)? ")
        choice = input().lower() or "no"
        if choice in ["yes", "no"]:
            break

    if choice == "no":
        return

    if not (trash := Path("trash")).exists():
        trash.mkdir()

    for new, old in renamings.items():
        old.rename(new)

    for new, old in deletions.items():
        old.rename(ensure(new))
        # location.unlink()

    _print("Files have been renamed and moved to trash")


def quit(input_before_exit=True, **kwargs):
    if input_before_exit:
        input("Press any key to exit...")
    exit(0)


def delete_duplicates(**config):
    _print(f"\n> Looking for duplicate files in folder '{config['root']}' ...\n")

    dry_run = config.get("dry_run", False)
    if dry_run:
        _print("    --- Dry run ---\n")

    _print(f"    Suffixes: {suffixes}\n")

    compute_hashes(**config)
    handle_duplicates(**config)
    shorten_names_of_other_files(**config)
    summarize(**config)
    apply_changes(**config)


if __name__ == "__main__":
    setup_logs()

    args = parser.parse_args()

    root = Path(args.directory)

    if not root.exists():
        _print(f"Error: The directory '{root}' doesn't exist")
        quit()

    config = {
        "root": root,
        "confirm": True,
        "dry_run": args.dry_run,
        "input_before_exit": not args.no_input_before_exit,
        "choose_original_name": args.choose_original_name,
    }

    delete_duplicates(**config)
    quit(**config)
