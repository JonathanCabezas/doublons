import re
import hashlib
import argparse
from shorten_regex import ShortenRegex
from pathlib import Path

# TODO compile regexes

# Parameters
suffixes = [" - Copie", " \(\d+\)"]


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
parser = argparse.ArgumentParser(description=description)
parser.add_argument(
    "--dry-run", action="store_true", help="List duplicate files without removing them"
)
parser.add_argument(
    "--interactive",
    action="store_true",
    help="Ask the user to choose which file to keep when there are multiple possible names",
)

# Global variables
shorten_regex = ShortenRegex(suffixes)
hash_to_locations = {}
files_to_handle = set()
number_of_duplicates = 0

DRY_RUN = False
INTERACTIVE = False


def hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()


def compute_hashes():
    for f in Path(".").glob("**/*"):
        if not f.is_file():
            continue

        files_to_handle.add(f)
        hash_to_locations.setdefault(hash(f), {})[f.name] = f


def handle_duplicates():
    global files_to_handle
    global number_of_duplicates

    for hash, name_to_locations in hash_to_locations.items():
        # If there are multiple locations for the same hash, we have duplicates
        if len(name_to_locations) == 1:
            continue

        number_of_duplicates += len(name_to_locations) - 1

        files_to_handle -= set(name_to_locations.values())
        # We shorten the names of the duplicate files to find all the possible original names
        posibles_names = []

        for name in name_to_locations.keys():
            shorter_name = shorten_regex.shorten(name)
            if shorter_name:
                name = shorter_name

            posibles_names.append(name)

        posibles_names = sorted(posibles_names)
        original = posibles_names[0]

        # If there are multiple possible names, we need to make a choice
        if any(posibles_names[0] != p for p in posibles_names):
            print(f"Hash {hash} has multiple posibles_names:")
            for i, p in enumerate(posibles_names):
                print(f" {i+1} - {p}")

            if INTERACTIVE:
                while True:
                    try:
                        choice = input(f"Please choose the correct one (1):")
                        if choice:
                            choice = int(choice) - 1
                            original = posibles_names[choice]
                        break
                    except:
                        pass
            else:
                print("Choosing the first one in alphabetical order")

        # When we have the original name, we check if the file already exists
        if original not in name_to_locations:
            print(f"Creating the file {Path(original)}")
        else:
            print(f"Keeping the file {name_to_locations[original]}")
            del name_to_locations[original]

        for location in name_to_locations.values():
            print(f"Removing the file {location}")
            if not DRY_RUN:
                location.unlink()

        print()


def shorten_names_of_other_files():
    print("\n> Shortening names of other files...\n")

    for f in files_to_handle:
        shorter_name = shorten_regex.shorten(f.name)

        if shorter_name:
            print(f"Renaming {f} to {f.with_name(shorter_name)}")
            if not DRY_RUN:
                f.rename(f.with_name(shorter_name))


if __name__ == "__main__":
    args = parser.parse_args()
    print("\n> Looking for duplicate files...\n")

    if args.dry_run:
        print("    --- Dry run ---\n")
        DRY_RUN = True

    if args.interactive:
        print("    --- Interactive mode ---\n")
        INTERACTIVE = True

    compute_hashes()
    handle_duplicates()
    shorten_names_of_other_files()