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

    KeywordNTIPAliasIDName      = auto()
    KeywordNTIPAliasName        = auto()
    KeywordNTIPAliasFlag        = auto()
    KeywordNTIPAliasQuality     = auto()
    KeywordNTIPAliasClass       = auto()
    KeywordNTIPAliasMaxQuantity = auto()
    KeywordNTIPAliasType        = auto()

    ValueNTIPAliasIDName        = auto()
    ValueNTIPAliasClass         = auto()
    ValueNTIPAliasClassID       = auto()
    ValueNTIPAliasFlag          = auto()
    ValueNTIPAliasQuality       = auto()
    ValueNTIPAliasStat          = auto()
    ValueNTIPAliasType          = auto()
    ValueNTIPAlias              = auto()

    WHITESPACE                  = auto()
    COMMENT                     = auto()

    SECTIONAND                  = auto()
    UNKNOWN                     = auto()



@dataclass
class Token:
    type: TokenType
    value: str | int

    def __repr__(self) -> str:
        return f"{self.type} : {self.value}"

    def data(self) -> dict:
        return {
            "type": self.type.name,
            "value": self.value
        }