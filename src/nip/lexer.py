from nip.NTIPAliasQuality import NTIPAliasQuality
from nip.NTIPAliasClass import NTIPAliasClass
from nip.NTIPAliasClassID import NTIPAliasClassID
from nip.NTIPAliasFlag import NTIPAliasFlag
from nip.NTIPAliasStat import NTIPAliasStat
from nip.NTIPAliasType import NTIPAliasType
from nip.tokens import Token, TokenType

from enum import Enum
from typing import Union, List
import re


WHITESPACE = " \t\n\r\v\f"
DIGITS = "0123456789.%"
SYMBOLS = [">", "=> ", "<", "<=", "=", "!", "", "", ",", "&", "|", "#", "/"]
MATH_SYMBOLS = ["(", ")", "^", "*", "/", "\\", "+", "-"]
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'"


class NipSections(Enum):
    PROP = 1
    STAT = 2
    MAXQUANTITY = 3

class NipSyntaxError(Exception):
    def __init__(self, message: str):
        self.message = message
        self.type = type
    
    def __str__(self):
        return self.message


class Lexer:
    def __init__(self):
        self.current_section: NipSections = NipSections.PROP
        self.current_token: Union[str, None] = ""
        self.text_i: int = -1
        self.tokens: List = []

    def increment_section(self):
        if self.current_section == NipSections.PROP:
            self.current_section = NipSections.STAT
        elif self.current_section == NipSections.STAT:
            self.current_section = NipSections.MAXQUANTITY


    def _advance(self):
        try:
            self.text_i += 1
            self.current_token = self.text[self.text_i]
        except IndexError:
            self.current_token = None


    def create_tokens(self, nip_expression):
        self.text = list(nip_expression)
        self._advance()
        self.tokens = []
        while self.current_token != None:
            if self.current_token in DIGITS:
                self.tokens.append(self._create_digits())
            elif self.current_token in WHITESPACE:
                self._advance()
            elif self.current_token in MATH_SYMBOLS:
                self.tokens.append(self._create_math_operator())
            elif self.current_token in SYMBOLS:
                self.tokens.append(self._create_logical_operator())
                # self.advance()
            elif self.current_token == "[":
                self.tokens.append(self._create_nip_lookup())
            elif self.current_token in CHARS:
                self.tokens.append(self._create_d2r_image_data_lookup())
            else:
                raise NipSyntaxError("Unknown token: " + self.current_token)
        return self.tokens

    def _create_digits(self):
        dot_count = 0
        n_str = self.current_token
        self._advance()
        while self.current_token != None and self.current_token in DIGITS:
            if self.current_token == ".":
                if dot_count >= 1:
                    break
                dot_count += 1
            n_str += self.current_token
            if self.current_token == "%":
                self._advance()
                break
            self._advance()
        if n_str.startswith("."):
            n_str = "0" + n_str
        elif n_str.endswith("."):
            n_str = n_str + "0"
        elif n_str.endswith("%"):
            if n_str != None:
                return Token(TokenType.NUMBERPERCENT, n_str[:-1])
        return Token(TokenType.NUMBER, float(n_str))


    def _create_math_operator(self):
        symbol = self.current_token
        self._advance()
        symbol_map = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '\\': TokenType.MODULO,
            '^': TokenType.POW
        }
        while self.current_token != None:

            if symbol == "+":
                return Token(TokenType.PLUS, symbol)
            elif symbol == "-":
                return Token(TokenType.MINUS, symbol)
            elif symbol == "*":
                return Token(TokenType.MULTIPLY, symbol)
            elif symbol == "/":
                return Token(TokenType.DIVIDE, symbol)
            elif symbol == "\\":
                return Token(TokenType.MODULO, symbol)
            elif symbol == "^":
                return Token(TokenType.POW, symbol)
            elif symbol == "(":
                return Token(TokenType.LPAREN, symbol)
            elif symbol == ")":
                return Token(TokenType.RPAREN, symbol)
        if symbol == "(":
            return Token(TokenType.LPAREN, symbol)
        elif symbol == ")":
            return Token(TokenType.RPAREN, symbol)


    def _create_nip_lookup(self):
        """
            item data lookup i.e [name]
        """
        self._advance()
        lookup_key = self.current_token
        while self.current_token != None:

            self._advance()
            if self.current_token == "]":
                break
            if lookup_key and self.current_token:
                lookup_key += self.current_token
        self._advance()

        if self.current_section == NipSections.PROP:
            if lookup_key:
                if lookup_key in "name":
                    return Token(TokenType.NAME, lookup_key)
                elif lookup_key == "flag":
                    return Token(TokenType.FLAG, lookup_key)
                elif lookup_key == "class":
                    return Token(TokenType.CLASS, lookup_key)
                elif lookup_key == "quality":
                    return Token(TokenType.QUALITY, lookup_key)
                elif lookup_key == "type":
                    return Token(TokenType._TYPE, lookup_key)
                elif lookup_key == "idname":
                    return Token(TokenType.IDNAME, lookup_key)
                elif lookup_key in NTIPAliasClass:
                    return Token(TokenType.NTIPAliasClass, NTIPAliasClass[lookup_key])
                elif lookup_key in NTIPAliasQuality:
                    return Token(TokenType.NTIPAliasQuality, NTIPAliasQuality[lookup_key])
                elif lookup_key in NTIPAliasClassID:
                    return Token(TokenType.NTIPAliasClassID, NTIPAliasClassID[lookup_key])
                elif lookup_key in NTIPAliasFlag:
                    return Token(TokenType.NTIPAliasFlag, NTIPAliasFlag[lookup_key])
                elif lookup_key in NTIPAliasType:
                    return Token(TokenType.NTIPAliasType, NTIPAliasType[lookup_key])
                else:
                    return Token(TokenType.UNKNOWN, "-1")
        elif self.current_section == NipSections.STAT:
            if lookup_key in NTIPAliasStat:
                return Token(TokenType.NTIPAliasStat, NTIPAliasStat[lookup_key])
            else:
                return Token(TokenType.UNKNOWN, "-1")
        elif self.current_section == NipSections.MAXQUANTITY:
            if lookup_key == "maxquanity":
                return Token(TokenType.MAXQUANITY, lookup_key)
            else:
                return Token(TokenType.UNKNOWN, "-1")

    def _create_d2r_image_data_lookup(self):
        lookup_key = self.current_token
        while self.current_token != None:
            self._advance()
            if self.current_token == None or self.current_token not in CHARS:
                break
            if self.current_token == "'":
                self.current_token = "\\'" # TODO FIX THIS (make stuff like diablo'shorn work..)
            if lookup_key and self.current_token:
                lookup_key += self.current_token
        # Converts stuff like ethereal to NTIPAliasFlag['ethereal']
        if self.current_section == NipSections.PROP:
            if lookup_key in NTIPAliasClass:
                return Token(TokenType.NTIPAliasClass, lookup_key)
            elif lookup_key in NTIPAliasQuality:
                return Token(TokenType.NTIPAliasQuality, lookup_key)
            elif lookup_key in NTIPAliasClassID and self.tokens[-2].type == TokenType.NAME:
                return Token(TokenType.NTIPAliasClassID, lookup_key)
            elif lookup_key in NTIPAliasFlag:
                return Token(TokenType.NTIPAliasFlag, lookup_key)
            elif lookup_key in NTIPAliasType:
                return Token(TokenType.NTIPAliasType, lookup_key)
            else:
                return Token(TokenType.UNKNOWN, lookup_key)
        elif self.current_section == NipSections.STAT:
            if lookup_key in NTIPAliasStat:
                return Token(TokenType.NTIPAliasStat, lookup_key)
            else:
                return Token(TokenType.UNKNOWN, "-1")
        


    def _create_logical_operator(self):
        char = self.current_token
        self._advance()
        logical_operator_map = {
            ">": TokenType.GT,
            "<": TokenType.LT,

            ">=": TokenType.GE,
            "<=": TokenType.LE,

            "==": TokenType.EQ,
            "!=": TokenType.NE,
       
            "&&": TokenType.AND,
            "||": TokenType.OR,

            "#": TokenType.SECTIONAND
        }

        pattern = "(>=|<=|==|!=|&&|\|\||>|<|\#)"
        get_text = "".join(self.text[self.text_i - 2:])

        res = re.search(pattern, get_text)
        if char:
            if res == None or char not in res.group(0):
                raise NipSyntaxError(f"Invalid logical operator: '{char}'")
        
        start, stop = 0, 0
        if res:
            start, stop = res.span()
        
        is_valid_relation_operator = True
        invalid_char = ''

        if get_text[start - 1] in SYMBOLS:
            is_valid_relation_operator = False
            invalid_char = get_text[start - 1]
        elif get_text[stop] in SYMBOLS:
            is_valid_relation_operator = False
            invalid_char = get_text[stop]

        if is_valid_relation_operator:
            if res:
                operator = res.group()
                for _ in range(start, stop):
                    self._advance()
                if operator == "#":
                    self.increment_section()
                
                pythonic_relation_operator = operator.replace("&&", "and").replace("||", "or")

                return Token(logical_operator_map[operator], pythonic_relation_operator)
        else:
            raise NipSyntaxError(f"Unexpected logical operator {invalid_char}")
        