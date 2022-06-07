from logger import Logger
from nip.NTIPAliasQuality import NTIPAliasQuality
from nip.NTIPAliasClass import NTIPAliasClass
from nip.NTIPAliasClassID import NTIPAliasClassID
from nip.NTIPAliasFlag import NTIPAliasFlag
from nip.NTIPAliasStat import NTIPAliasStat
from nip.NTIPAliasType import NTIPAliasType
from nip.tokens import Token, TokenType

from enum import Enum
from typing import List
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
        self.current_token: str | None = ""
        self.text_i: int = -1
        self.tokens: List = []

    def increment_section(self):
        if self.current_section == NipSections.PROP:
            self.current_section = NipSections.STAT
        elif self.current_section == NipSections.STAT:
            self.current_section = NipSections.MAXQUANTITY

    def get_current_iteration_of_text_raw(self):
        """
            Returns the self.text in a string type, and at its current iteration.
        """
        return "".join(self.text[self.text_i:])

    def _advance(self):
        try:
            self.text_i += 1
            self.current_token = self.text[self.text_i]
        except IndexError:
            self.current_token = None


    def create_tokens(self, nip_expression, starting_section: NipSections = NipSections.PROP):
        self.current_section = starting_section
        self.text = list(nip_expression)
        self._advance()
        self.tokens = []
        while self.current_token != None:
            if self.current_token in DIGITS:
                self.tokens.append(self._create_digits())
            elif self.current_token in WHITESPACE:
                self._advance()
            elif self.current_token in SYMBOLS:
                self.tokens.append(self._create_logical_operator())
            elif self.current_token in MATH_SYMBOLS:
                self.tokens.append(self._create_math_operator())
                self._advance()
                # self.advance()
            elif self.current_token == "[":
                self.tokens.append(self._create_nip_lookup())
            elif self.current_token in CHARS:
                self.tokens.append(self._create_d2r_image_data_lookup())
            else:
                raise NipSyntaxError("Unknown token: " + self.current_token)
        return self.tokens

    def _create_custom_digit_token(self, found_number, append_text="", append_front=False):
        """
            Creates a custom token for a number that allows for custom text to be appended to the front or back of the found number.
        """
        for _ in range(len(found_number)):
            self._advance()
        if append_text:
            if append_front:
                found_number = append_text + found_number
            else:
                found_number += append_text
        
        return Token(TokenType.NUMBER, float(found_number))

    def _create_digits(self):
        found_decimal_number = re.match(r"^[0-9]+\.[0-9]+", self.get_current_iteration_of_text_raw())
        if found_decimal_number:
            return self._create_custom_digit_token(found_decimal_number.group(0))

        shorthand_decimal_number = re.match(r"^\.[0-9]+", self.get_current_iteration_of_text_raw())
        if shorthand_decimal_number:
            return self._create_custom_digit_token(shorthand_decimal_number.group(0), "0", append_front=True)

        found_whole_number = re.match(r"^[0-9]+", self.get_current_iteration_of_text_raw())
        if found_whole_number:
            return self._create_custom_digit_token(found_whole_number.group(0))


    def _create_math_operator(self):
        symbol = self.current_token
        symbol_map = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '\\': TokenType.MODULO,
            '^': TokenType.POW,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN
        }

        if symbol in symbol_map:
            return Token(symbol_map[symbol], symbol)
        return Token(TokenType.UNKNOWN, symbol)

    def _create_nip_lookup(self):
        """
            item data lookup i.e [name]
        """
        lookup_key = ""
        if self.text:
            found_match = re.match(r"\[\w+\]|\[d+\]", self.get_current_iteration_of_text_raw()) # Finds the first match of [word] or [21234223892] (numbers :P)
            if found_match:
                found = found_match.group(0)
                for char in found:
                    if char.isalnum(): # is alpha numeric
                        lookup_key += char
                    self._advance()

        if self.current_section == NipSections.PROP:
            if lookup_key:
                match lookup_key:
                    case "name":
                        return Token(TokenType.KeywordNTIPAliasName, lookup_key)
                    case "flag":
                        return Token(TokenType.KeywordNTIPAliasFlag, lookup_key)
                    case "class":
                        return Token(TokenType.KeywordNTIPAliasClass, lookup_key)
                    case "quality":
                        return Token(TokenType.KeywordNTIPAliasQuality, lookup_key)
                    case "type":
                        return Token(TokenType.KeywordNTIPAliasType, lookup_key)
                    case "idname":
                        return Token(TokenType.KeywordNTIPAliasIDName, lookup_key)
                    case _: # ? This is default.. 
                        if lookup_key in NTIPAliasClass:
                            return Token(TokenType.ValueNTIPAliasClass, NTIPAliasClass[lookup_key])
                        elif lookup_key in NTIPAliasQuality:
                            return Token(TokenType.ValueNTIPAliasQuality, NTIPAliasQuality[lookup_key])
                        elif lookup_key in NTIPAliasClassID:
                            return Token(TokenType.ValueNTIPAliasClassID, NTIPAliasClassID[lookup_key])
                        elif lookup_key in NTIPAliasFlag:
                            return Token(TokenType.ValueNTIPAliasFlag, NTIPAliasFlag[lookup_key])
                        elif lookup_key in NTIPAliasType:
                            return Token(TokenType.ValueNTIPAliasType, NTIPAliasType[lookup_key])
                Logger.warning("Unknown property lookup: " + lookup_key + " " + "".join(self.text))
                return Token(TokenType.UNKNOWN, "-1")
        elif self.current_section == NipSections.STAT:
            if lookup_key in NTIPAliasStat:
                return Token(TokenType.ValueNTIPAliasStat, NTIPAliasStat[lookup_key])
            else:
                Logger.warning("Unknown NTIP stat lookup: " + lookup_key)
                return Token(TokenType.UNKNOWN, "-1")
        elif self.current_section == NipSections.MAXQUANTITY:
            pass
               

    def _create_d2r_image_data_lookup(self):
        lookup_key = ""
        
        found_lookup_key = re.match(r"^(\w+)\s*", self.get_current_iteration_of_text_raw())
        if found_lookup_key:
            found = found_lookup_key.group(1).replace("'", "\\'") # Replace ' with escaped \'
            for _ in range(len(found)):
                self._advance()
            lookup_key = found

        if self.current_section == NipSections.PROP: 
            # TODO: The second checks (i.e NTIPAliasClass and self.tokens[-2].type == TokenType.CLASS:) seem a little misplaced, possibly put them inside the validation function that is inside transpiler.py and throw a warning accordingly.
            if lookup_key in NTIPAliasClass and self.tokens[-2].type == TokenType.KeywordNTIPAliasClass:
                return Token(TokenType.ValueNTIPAliasClass, lookup_key)
            elif lookup_key in NTIPAliasQuality and self.tokens[-2].type == TokenType.KeywordNTIPAliasQuality:
                return Token(TokenType.ValueNTIPAliasQuality, lookup_key)
            elif lookup_key in NTIPAliasClassID and self.tokens[-2].type == TokenType.KeywordNTIPAliasName:
                return Token(TokenType.ValueNTIPAliasClassID, lookup_key)
            elif lookup_key in NTIPAliasFlag and self.tokens[-2].type == TokenType.KeywordNTIPAliasFlag:
                return Token(TokenType.ValueNTIPAliasFlag, lookup_key)
            elif lookup_key in NTIPAliasType and self.tokens[-2].type == TokenType.KeywordNTIPAliasType:
                return Token(TokenType.ValueNTIPAliasType, lookup_key)
            else:
                return Token(TokenType.UNKNOWN, lookup_key)
        elif self.current_section == NipSections.STAT:
            if lookup_key in NTIPAliasStat:
                return Token(TokenType.ValueNTIPAliasStat, lookup_key)
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

        pattern = r"(>=|<=|==|!=|&&|\|\||>|<|\#)"
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
