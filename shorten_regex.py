import re


class ShortenRegex:
    """
    The ShortenRegex class
    """

    def __init__(self, matches):
        self.regexes = [f"(.*){match}(\..*)" for match in matches]

    def shorten_once(self, str):
        for regex in self.regexes:
            if m := re.search(regex, str):
                return "".join(m.groups())

        return None

    def shorten(self, str):
        shortened = False

        while shorter_str := self.shorten_once(str):
            str = shorter_str
            shortened = True

        if shortened:
            return str

        return None
