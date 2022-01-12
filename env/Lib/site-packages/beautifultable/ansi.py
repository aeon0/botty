"""Module Containing class required for handling ANSI and east asian chars"""

from __future__ import unicode_literals


import re

try:
    from wcwidth import wcwidth
except ImportError:  # pragma: no cover
    wcwidth = len  # pragma: no cover

from .compat import to_unicode


class ANSIMultiByteString(object):

    ANSI_REGEX = re.compile(
        r"(\x1B(?:[()][AB012]|[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]))"
    )
    ANSI_RESET = "\x1b[0m"

    def __init__(self, string):
        self._string = []
        self._state = []
        self._width = []
        self._termwidth = 0

        state = set()

        for token in re.split(self.ANSI_REGEX, to_unicode(string)):
            if token:
                if re.match(self.ANSI_REGEX, token):
                    if token == self.ANSI_RESET:
                        state.clear()
                    else:
                        state.add(token)
                else:
                    s_copy = set(state)
                    for char in token:
                        w = wcwidth(char)
                        if w == -1:
                            raise ValueError(
                                (
                                    "Unsupported Literal {} in " "string {}"
                                ).format(repr(char), repr(token))
                            )
                        self._termwidth += w
                        self._string.append(char)
                        self._width.append(w)
                        self._state.append(s_copy)

    def __len__(self):
        return len(self._string)

    def __getitem__(self, key):
        if isinstance(key, int):
            if self._state[key]:
                return (
                    "".join(self._state[key])
                    + self._string[key]
                    + self.ANSI_RESET
                )
            return self._string[key]
        if isinstance(key, slice):
            return self._slice(key)
        raise TypeError(
            ("table indices must be integers or slices, " "not {}").format(
                type(key).__name__
            )
        )

    def _slice(self, key):
        res = []
        prev_state = set()
        for char, state in zip(self._string[key], self._state[key]):
            if prev_state == state:
                pass
            elif prev_state <= state:
                res.extend(state - prev_state)
            else:
                res.append(self.ANSI_RESET)
                res.extend(state)
            prev_state = state
            res.append(char)
        if prev_state:
            res.append(self.ANSI_RESET)
        return "".join(res)

    def termwidth(self):
        """Returns the width of string as when printed to a terminal"""
        return self._termwidth

    def wrap(self, width):
        """Returns a partition of the string based on `width`"""
        res = []
        prev_state = set()
        part = []
        cwidth = 0
        for char, _width, state in zip(self._string, self._width, self._state):
            if cwidth + _width > width:
                if prev_state:
                    part.append(self.ANSI_RESET)
                res.append("".join(part))
                prev_state = set()
                part = []
                cwidth = 0
            cwidth += _width
            if prev_state == state:
                pass
            elif prev_state <= state:
                part.extend(state - prev_state)
            else:
                part.append(self.ANSI_RESET)
                part.extend(state)
            prev_state = state
            part.append(char)
        if prev_state:
            part.append(self.ANSI_RESET)
        if part:
            res.append("".join(part))
        return res
