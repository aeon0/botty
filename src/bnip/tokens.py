from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

class TokenType(Enum):
    NUMBER                      = auto()
    NUMBERPERCENT               = auto()
    PLUS                        = auto()
    MINUS                       = auto()
    MULTIPLY                    = auto()
    DIVIDE                      = auto()
    MODULO                      = auto()
    POW                         = auto()

    LPAREN                      = auto()
    RPAREN                      = auto()

    GT                          = auto()
    LT                          = auto()
    LE                          = auto()
    GE                          = auto()
    EQ                          = auto()
    NE                          = auto()
    AND                         = auto()
    OR                          = auto()

    KeywordNTIPAliasClass       = auto()
    KeywordNTIPAliasFlag        = auto()
    KeywordNTIPAliasIDName      = auto()
    KeywordNTIPAliasName        = auto()
    KeywordNTIPAliasQuality     = auto()
    KeywordNTIPAliasType        = auto()
    KeywordNTIPAliasStat        = auto()
    KeywordNTIPAliasMaxQuantity = auto()

    ValueNTIPAliasClass         = auto()
    ValueNTIPAliasClassID       = auto()
    ValueNTIPAliasFlag          = auto()
    ValueNTIPAliasIDName        = auto()
    ValueNTIPAliasQuality       = auto()
    ValueNTIPAliasStat          = auto()
    ValueNTIPAliasType          = auto()

    WHITESPACE                  = auto()
    COMMENT                     = auto()

    SECTIONAND                  = auto()

    NOTIFICATION                = auto()

    UNKNOWN                     = auto()

@dataclass
class Token:
    type: TokenType
    value: str | int | float

    def __repr__(self) -> str:
        return f"{self.type} : {self.value}"

    def data(self) -> dict:
        return {
            "type": self.type.name,
            "value": self.value
        }