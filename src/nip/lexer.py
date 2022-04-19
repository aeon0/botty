from nip.NTIPAliasQuality import NTIPAliasQuality
from nip.NTIPAliasClass import NTIPAliasClass
from nip.NTIPAliasClassID import NTIPAliasClassID
from nip.NTIPAliasFlag import NTIPAliasFlag
from nip.NTIPAliasStat import NTIPAliasStat
from nip.NTIPAliasType import NTIPAliasType

from nip.tokens import Token, TokenType
import json
from enum import Enum

WHITESPACE = " \t\n\r\v\f"
DIGITS = "0123456789.%"
SYMBOLS = [">", "=> ", "<", "<=", "=", "!", "", "", ",", "&", "|", "#", "/"]
MATH_SYMBOLS = ["(", ")", "^", "*", "/", "\\", "+", "-"]
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'"


class NipSections(Enum):
    PROP = 1
    STAT = 2
    MAXQUANTITY = 3


class Lexer:
    def __init__(self):
        self.current_section = NipSections.PROP

    def increment_section(self):
        if self.current_section == NipSections.PROP:
            self.current_section = NipSections.STAT
        elif self.current_section == NipSections.STAT:
            self.current_section = NipSections.MAXQUANTITY

    def create_tokens(self, nip_expression):
        self.text = iter(nip_expression)
        self._advance()
        while self.current_token != None:
            if self.current_token in DIGITS:
                yield self._create_digits()
            elif self.current_token in WHITESPACE:
                self._advance()
                # yield Token(TokenType.WHITESPACE, " ")
            elif self.current_token in SYMBOLS:
                yield self._create_logical_operator()
            elif self.current_token in MATH_SYMBOLS:
                yield self._create_math_operator()
                # self.advance()
            elif self.current_token == "[":
                yield self._create_nip_lookup()
            elif self.current_token in CHARS:
                yield self._create_d2r_image_data_lookup()

    
    def _advance(self):
        try:
            self.current_token = next(self.text)
        except StopIteration:
            self.current_token = None


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
        self._advance()
        lookup_key = self.current_token
        while self.current_token != None:
            self._advance()
            if self.current_token == "]":
                break
            lookup_key += self.current_token
        self._advance()

        if self.current_section == NipSections.PROP:
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
            lookup_key += self.current_token
        # Converts stuff like ethereal to NTIPAliasFlag['ethereal']
        if self.current_section == NipSections.PROP:
            if lookup_key in NTIPAliasClass:
                return Token(TokenType.NTIPAliasClass, lookup_key)
            elif lookup_key in NTIPAliasQuality:
                return Token(TokenType.NTIPAliasQuality, lookup_key)
            elif lookup_key in NTIPAliasClassID:
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
        while self.current_token != None:
            if char == ">":
                if self.current_token == "=":
                    self._advance()
                    return Token(TokenType.GE, ">=")
                else:
                    return Token(TokenType.GT, ">")
            elif char == "<":
                if self.current_token == "=":
                    self._advance()
                    return Token(TokenType.LE, "<=")
                else:
                    return Token(TokenType.LT, "<")
            elif char == "=":
                if self.current_token == "=":
                    self._advance()
                    return Token(TokenType.EQ, "==")
            elif char == "!":
                if self.current_token == "=":
                    self._advance()
                    return Token(TokenType.NE, "!=")
            elif char == "&":
                if self.current_token == "&":
                    self._advance()
                    return Token(TokenType.AND, "and")
            elif char == "#":
                # Increment the section.
                self.increment_section()
                return Token(TokenType.SECTIONAND, "and")
            elif char == "|":
                if self.current_token == "|":
                    self._advance()
                    return Token(TokenType.OR, "or")
            elif char == "/":
                if self.current_token == "/":
                    self._advance()
                    return Token(TokenType.COMMENT, "") # We don't really need comments in the transpiled version...
                else:
                    return Token(TokenType.DIVIDE, "/")
            else:
                # print("Unknown operator", char)
                break
        if char == "#":
            self.increment_section()
            return Token(TokenType.AND, "and")
        self._advance()