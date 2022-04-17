from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    NUMBER =              1
    NUMBERPERCENT =       2
    PLUS =                3
    MINUS =               4
    MULTIPLY =            5
    DIVIDE =              6
    MODULO =              7
    POW =                 8
    LPAREN =              9
    RPAREN =              10
    
    GT =                  11
    LT =                  12
    LE =                  13
    GE =                  14
    EQ =                  15
    NE =                  16
    AND =                 17
    OR =                  18

    NTIPAliasClass =      19
    NTIPAliasClassID =    20
    NTIPAliasFlag =       21
    NTIPAliasQuality =    22
    NTIPAliasStat =       23
    NTIPAliasType =       24
    NTIPAlias =           25

    NAME =                26
    FLAG =                27
    QUALITY =             28
    CLASS =               29
    MAXQUANITY =          30
    _TYPE =               31

    WHITESPACE =          32
    COMMENT =             33

    SECTIONAND =          35

    UNKNOWN =             36



@dataclass
class Token:
    type: TokenType
    value: any

    def __repr__(self) -> str:
        return f"{self.type} : {self.value}"