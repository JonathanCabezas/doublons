import re
import hashlib
import argparse
import igittigitt
from shorten_regex import ShortenRegex
from pathlib import Path

# Parameters
suffixes = [" - Copie", " \(\d+\)"]
ignore_parser = igittigitt.IgnoreParser()
ignore_parser.parse_rule_file(Path("ignorelist"))


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
    "--interactive",
    action="store_true",
    help="Ask the user to choose which file to keep when there are multiple possible names",
)
parser.add_argument(
    "--suffixes",
    nargs="+",
    help="List of suffixes to remove from the files",
    default=suffixes,
)

args = None

# Global variables
shorten_regex = ShortenRegex(suffixes)
hash_to_locations = {}
files_to_handle = set(
    [
        f
        for f in Path(".").glob("**/*")
        if f.is_file() and not ignore_parser.match(f)
    ]
)
number_of_duplicates = 0
number_of_files_to_shorten = 0

renamings = {}
deletions = {}


def hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()


def compute_hashes():
    n = len(files_to_handle)
    print(f"    Number of files to handle: {n}")

    for i, f in enumerate(files_to_handle):
        h = hash(f)
        hash_to_locations.setdefault(h, []).append(f)
        print(f"    ({i+1}/{n}) Hash of {f} is {h}", end="\r")

    print("\n")


def automatic_choice(posibles_names):
    # If a name starts with "IMG" or "VID", we choose it
    for i, p in enumerate(posibles_names):
        if p.startswith("IMG") or p.startswith("VID"):
            return i

    return 0


def schedule_renaming(location, new_location):
    global renamings
    if new_location.exists() or new_location in renamings:
        print(
            f"    The file '{new_location}' already exists with different content than '{location}'"
        )
        print(f"    Keeping the file '{location}'")
        return
    print(f"    Renaming the file '{location}' -> '{new_location}'")
    renamings[new_location] = location


def ensure(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def schedule_deletion(location):
    global deletions
    new_location = Path("Trash") / location
    print(f"    Moving the file '{location}' to '{new_location}'")
    deletions[new_location] = location


def handle_duplicates():
    global files_to_handle, number_of_duplicates, renamings, deletions

    for hash, locations in hash_to_locations.items():
        # If there are multiple locations for the same hash, we have duplicates
        if len(locations) == 1:
            continue

        print(f"> Hash {hash} has duplicates:\n")
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
            print(f"  There are multiple posibles_names:")
            for i, p in enumerate(posibles_names):
                print(f"    {i+1} - {p}")

            if args.interactive:
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
            print()

        original = posibles_names[choice]
        print(f"  Choosing the name '{original}' as the original name\n")

        # We detect files with the same name
        name_to_locations = {}
        for location in locations:
            name = location.name
            if name in name_to_locations:
                print(
                    f"  The file '{location}' has the same name as '{name_to_locations[name]}'\n"
                )
                if location < name_to_locations[name]:
                    schedule_deletion(name_to_locations[name])
                else:
                    schedule_deletion(location)
                    continue

            name_to_locations[name] = location

        # When we have the original name, we check if the file already exists
        if original not in name_to_locations:
            location = name_to_locations.popitem()[1]
            new_location = Path(original)
            schedule_renaming(location, new_location)
        else:
            print(f"    Keeping the file '{name_to_locations[original]}'")
            del name_to_locations[original]

        # Deleting all the other files
        for location in name_to_locations.values():
            schedule_deletion(location)

        print()


def shorten_names_of_other_files():
    global renamings, number_of_files_to_shorten
    print("\n> Shortening names of other files...\n")

    for f in files_to_handle:
        shorter_name = shorten_regex.shorten(f.name)

        if shorter_name:
            number_of_files_to_shorten += 1
            schedule_renaming(f, f.with_name(shorter_name))


def summarize():
    print(f"\n> Summary:\n")
    print(f"    Number of duplicates: {number_of_duplicates}")
    print(f"    Number of files to shorten: {number_of_files_to_shorten}")
    print(f"    Number of files to delete: {len(deletions)}")
    print(f"    Number of files to rename: {len(renamings)}")


def apply_changes(confirm=True):
    if args.dry_run:
        return

    while True and confirm:
        print("\nAre you sure you want to continue (yes/NO)? ")
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

    print("Files have been renamed and moved to trash")


def quit():
    input("Press any key to exit...")
    exit(0)


def delete_duplicates(confirm=True):
    compute_hashes()
    handle_duplicates()
    shorten_names_of_other_files()
    summarize()
    apply_changes(confirm)
    quit()


if __name__ == "__main__":
    args = parser.parse_args()
    print("\n> Looking for duplicate files...\n")

    if args.dry_run:
        print("    --- Dry run ---\n")

    if args.interactive:
        print("    --- Interactive mode ---\n")

    if args.suffixes:
        suffixes = args.suffixes
        print(f"    Suffixes: {suffixes}\n")

    delete_duplicates()
