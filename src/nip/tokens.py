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

    IDNAME =              26
    NAME =                27
    FLAG =                28
    QUALITY =             29
    CLASS =               30
    MAXQUANITY =          31
    _TYPE =               32

    WHITESPACE =          33
    COMMENT =             34

    SECTIONAND =          35

    UNKNOWN =             36



@dataclass
class Token:
    type: TokenType
    value: any

    def __repr__(self) -> str:
        return f"{self.type} : {self.value}"