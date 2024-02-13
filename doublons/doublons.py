import mio
import logging
import hashlib
import argparse

from filter import Filter
from pathlib import Path
from shorten_regex import ShortenRegex

# Parameters
VERSION = "1.0.2"

suffixes = [" - Copie", r" \(\d+\)"]
white_list = Filter(Path(__file__).parent / Path("whitelist"))
black_list = Filter(Path(__file__).parent / Path("blacklist"))


# A multiple lines string description with an example of the program
description = """This program finds duplicates files in a directory and removes them.
For example, if you have the following files:
- test.txt
- test - Copie.txt
- test (2).txt
The program will remove the last 2 files if they have the same content as the first one.
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
    help="Ask the user to choose the original name of the file when there are multiple "
    "possible names",
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
hash_to_locations: dict[str, list[Path]] = {}
files_to_handle: set[Path] | None = None
number_of_duplicates = 0
number_of_files_to_shorten = 0

renamings: dict[str, str] = {}
deletions: dict[str, str] = {}


def hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()


def compute_hashes(root, **kwargs):
    global files_to_handle

    with mio.Section("Computing hashes..."):
        files_to_handle = set(
            [
                f
                for f in root.glob("**/*")
                if f.is_file() and white_list.accept(f) and black_list.accept(f)
            ]
        )
        n = len(files_to_handle)
        logging.info("Number of files to handle: {}", n)

        for i, f in enumerate(files_to_handle):
            logging.info("({}/{}) Computing hash of {}", i + 1, n, f)
            h = hash(f)
            hash_to_locations.setdefault(h, []).append(f)
            logging.info("Hash: {}", h)


def automatic_choice(possible_names):
    # If a name starts with "IMG" or "VID", we choose it
    for i, p in enumerate(possible_names):
        if p.startswith("IMG") or p.startswith("VID"):
            return i

    return 0


def schedule_renaming(location, new_location):
    global renamings
    if new_location.exists() or new_location in renamings:
        logging.info(
            "The file {} already exists with different content than {}",
            new_location,
            location,
        )
        logging.info("Keeping the file {}", location)
        return
    logging.info("Renaming the file {} -> {}", location, new_location)
    renamings[new_location] = location


def ensure(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def schedule_deletion(location):
    global deletions
    new_location = Path("Trash") / location
    logging.info("Moving the file {} to {}", location, new_location)
    deletions[new_location] = location


def handle_duplicates(root, choose_original_name=False, **kwargs):
    global files_to_handle, number_of_duplicates, renamings, deletions

    for hash, locations in hash_to_locations.items():
        # If there are multiple locations for the same hash, we have duplicates
        if len(locations) == 1:
            continue

        with mio.Section("Hash {} has duplicates", hash):
            number_of_duplicates += len(locations) - 1
            files_to_handle -= set(locations)

            # We shorten the names of the duplicate files
            # # to find all the possible original names
            possible_names = []
            for location in locations:
                name = location.name
                if name in possible_names:
                    continue

                shorter_name = shorten_regex.shorten(name)
                if shorter_name:
                    name = shorter_name

                possible_names.append(name)
            possible_names = sorted(possible_names)
            choice = 0

            # If there are multiple possible names, we need to make a choice
            if any(possible_names[0] != p for p in possible_names):
                logging.info("Multiple possible names: ")
                for i, p in enumerate(possible_names):
                    logging.info("    " + str(i + 1) + " - {}", p)

                if choose_original_name:
                    while True:
                        try:
                            choice = input("  Please choose the correct one (1):")
                            if choice:
                                choice = int(choice) - 1
                                if choice < 0 or choice >= len(possible_names):
                                    raise ValueError
                            break
                        except Exception:
                            pass
                else:
                    choice = automatic_choice(possible_names)
                logging.info("")

            original = possible_names[choice]
            logging.info("Choosing the name {} as the original name", original)

            # We detect files with the same name
            name_to_locations = {}
            for location in locations:
                name = location.name
                if name in name_to_locations:
                    logging.info(
                        "The file {} has the same name as {}",
                        location,
                        name_to_locations[name],
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
                logging.info("Keeping the file {}", name_to_locations[original])
                del name_to_locations[original]

            # Deleting all the other files
            for location in name_to_locations.values():
                schedule_deletion(location)

            logging.info("")


def shorten_names_of_other_files(**kwargs):
    global renamings, number_of_files_to_shorten
    with mio.Section("Shortening names of other files..."):
        for f in files_to_handle:
            shorter_name = shorten_regex.shorten(f.name)

            if shorter_name:
                number_of_files_to_shorten += 1
                schedule_renaming(f, f.with_name(shorter_name))


def summarize(**kwargs):
    with mio.Section("Summary"):
        logging.info("Number of duplicates: {}", number_of_duplicates)
        logging.info("Number of files to shorten: {}", number_of_files_to_shorten)
        logging.info("Number of files to delete: {}", len(deletions))
        logging.info("Number of files to rename: {}", len(renamings))


def apply_changes(dry_run=False, confirm=True, **kwargs):
    if dry_run:
        return

    choice = "yes"
    while True and confirm:
        logging.info("Are you sure you want to continue (yes/NO)?")
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

    logging.info("Files have been renamed and moved to trash successfully")


def delete_duplicates(**config):
    logging.info("Looking for {}", "duplicate files")
    logging.info("Folder: {}", "Current" if config["root"] == "." else config["root"])
    dry_run = config.get("dry_run", False)
    if dry_run:
        logging.info("    --- Dry run ---\n")

    logging.info("Suffixes: {}", str(suffixes))

    compute_hashes(**config)
    handle_duplicates(**config)
    shorten_names_of_other_files(**config)
    summarize(**config)
    apply_changes(**config)


if __name__ == "__main__":
    mio.install_logger("doublons.log", False)

    args = parser.parse_args()

    if not args.no_input_before_exit:
        mio.add_confirmation_text_at_exit("Press any key to exit...")

    root = Path(args.directory)

    if not root.exists():
        logging.critical("The directory '{}' doesn't exist", root)

    config = {
        "root": root,
        "confirm": True,
        "dry_run": args.dry_run,
        "choose_original_name": args.choose_original_name,
    }

    delete_duplicates(**config)
