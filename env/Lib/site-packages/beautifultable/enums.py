from __future__ import unicode_literals
import enum

from .styles import (
    DefaultStyle,
    NoStyle,
    DottedStyle,
    MySQLStyle,
    SeparatedStyle,
    CompactStyle,
    MarkdownStyle,
    RestructuredTextStyle,
    BoxStyle,
    DoubledBoxStyle,
    RoundedStyle,
    GridStyle,
)


class WidthExceedPolicy(enum.Enum):
    WEP_WRAP = 1
    WEP_STRIP = 2
    WEP_ELLIPSIS = 3

    def __repr__(self):
        return self.name


class SignMode(enum.Enum):
    SM_PLUS = "+"
    SM_MINUS = "-"
    SM_SPACE = " "

    def __repr__(self):
        return self.name


class Alignment(enum.Enum):
    ALIGN_LEFT = "<"
    ALIGN_CENTER = "^"
    ALIGN_RIGHT = ">"

    def __repr__(self):
        return self.name


class Style(enum.Enum):
    STYLE_DEFAULT = DefaultStyle
    STYLE_NONE = NoStyle
    STYLE_DOTTED = DottedStyle
    STYLE_MYSQL = MySQLStyle
    STYLE_SEPARATED = SeparatedStyle
    STYLE_COMPACT = CompactStyle
    STYLE_MARKDOWN = MarkdownStyle
    STYLE_RST = RestructuredTextStyle
    STYLE_BOX = BoxStyle
    STYLE_BOX_DOUBLED = DoubledBoxStyle
    STYLE_BOX_ROUNDED = RoundedStyle
    STYLE_GRID = GridStyle

    def __repr__(self):
        return self.name


WEP_WRAP = WidthExceedPolicy.WEP_WRAP
WEP_STRIP = WidthExceedPolicy.WEP_STRIP
WEP_ELLIPSIS = WidthExceedPolicy.WEP_ELLIPSIS
SM_PLUS = SignMode.SM_PLUS
SM_MINUS = SignMode.SM_MINUS
SM_SPACE = SignMode.SM_SPACE
ALIGN_LEFT = Alignment.ALIGN_LEFT
ALIGN_CENTER = Alignment.ALIGN_CENTER
ALIGN_RIGHT = Alignment.ALIGN_RIGHT
STYLE_DEFAULT = Style.STYLE_DEFAULT
STYLE_NONE = Style.STYLE_NONE
STYLE_DOTTED = Style.STYLE_DOTTED
STYLE_SEPARATED = Style.STYLE_SEPARATED
STYLE_COMPACT = Style.STYLE_COMPACT
STYLE_MYSQL = Style.STYLE_MYSQL
STYLE_MARKDOWN = Style.STYLE_MARKDOWN
STYLE_RST = Style.STYLE_RST
STYLE_BOX = Style.STYLE_BOX
STYLE_BOX_DOUBLED = Style.STYLE_BOX_DOUBLED
STYLE_BOX_ROUNDED = Style.STYLE_BOX_ROUNDED
STYLE_GRID = Style.STYLE_GRID
