import re

from enum import Enum
from pathlib import Path

FilterType = Enum("FilterType", ["NONE", "WHITE", "BLACK"])


class Filter:
    def __init__(self, file_path: Path, type: FilterType = FilterType.NONE):
        self.regexes = self.import_list(file_path)

        if type is FilterType.NONE:
            if "white" in file_path.stem:
                self.type = FilterType.WHITE
            elif "black" in file_path.stem:
                self.type = FilterType.BLACK
            else:
                raise ValueError("No filter type specified")
        else:
            self.type = type

    def import_list(self, file_path: Path) -> list[re.Pattern]:
        regexes: list[re.Pattern] = []
        with file_path.open() as f:
            while line := f.readline():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                line = (
                    line.replace(".", r"\.")
                    .replace("**/", r"([^/]+/)#STAR#")
                    .replace("*", r"[^/]+")
                    .replace("#STAR#", r"*")
                )
                regexes.append(re.compile(line))

        return regexes

    # A white filter will accept a path if it matches any of the regexes
    # A black filter will reject a path if it matches any of the regexes
    def accept(self, path: Path) -> bool:
        if r"playground\.picasa.ini" in str(path):
            pass
        for regex in self.regexes:
            if regex.match(path.as_posix()):
                return self.type == FilterType.WHITE
        return self.type == FilterType.BLACK
