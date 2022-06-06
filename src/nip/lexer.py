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
        """
            Increments the self.current_section to the next section.
        """
        if self.current_section == NipSections.PROP:
            self.current_section = NipSections.STAT
        elif self.current_section == NipSections.STAT:
            self.current_section = NipSections.MAXQUANTITY


    def _advance(self):
        """
            Advances the self.text_i and self.current_token.
        """
        try:
            self.text_i += 1
            self.current_token = self.text[self.text_i]
        except IndexError:
            self.current_token = None

    def get_current_iteration_of_text_raw(self):
        """
            Returns the self.text in a string type, and at its current iteration.
        """
        return "".join(self.text[self.text_i:])
 
       
    def create_tokens(self, nip_expression, starting_section=NipSections.PROP):
        """
            Creates the tokens for the nip_expression.
        """
        self.text = list(nip_expression)
        self._advance()
        self.tokens = []
        self.current_section = starting_section
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
        """
            Creates a token for a digit.
        """
        dot_count = 0
        n_str = self.current_token
        self._advance()
        if n_str:
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
        """
            Creates a token for a math operator.
        """
        symbol = self.current_token
        self._advance()
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

        while self.current_token != None:
            if self.current_token in symbol_map:
                if symbol:
                    return Token(symbol_map[symbol], symbol)


    def _create_nip_lookup(self):
        """
            Create a token for a nip lookup.
            item data lookup i.e [name]
        """

        self._advance() # Increment past the [
        lookup_key = ""

        # Now it should look something like this "lookup_key]"

        if self.text:
            found_match = re.match(r"(\w+])|(\d+)]", self.get_current_iteration_of_text_raw()) # Find the lookup_key]
            if found_match and found_match.group(1):
                found = found_match.group(1)#.replace("]", "") # Remove the closing bracket.
                for i in range(len(found)):
                    if found[i] != "]": # * We don't want to add the closing bracket in our lookup_key...
                        lookup_key += found[i]
                    self._advance()

        allowed_NTIPAliases = { # * Allows NTIP operators to be used within certain sections.
            # * For example, [name] is allowed in the PROP section, and is [flag] too. Also everything inside NTIPAliasClass, NTIPAliasQuality dicts ect is allowed inside props.
            NipSections.PROP: [
                ["name", TokenType.NAME],
                ["flag", TokenType.FLAG],
                ["class", TokenType.CLASS],
                ["quality", TokenType.QUALITY],
                ["type", TokenType._TYPE],
                ["idname", TokenType.IDNAME],

                [NTIPAliasClass, TokenType.NTIPAliasClass],
                [NTIPAliasQuality, TokenType.NTIPAliasQuality],
                [NTIPAliasClassID, TokenType.NTIPAliasClassID],
                [NTIPAliasFlag, TokenType.NTIPAliasFlag],
                [NTIPAliasType, TokenType.NTIPAliasType],
            ],

            NipSections.STAT: [
                [NTIPAliasStat, TokenType.NTIPAliasStat]
            ],

            NipSections.MAXQUANTITY: [
                ["maxquanity", TokenType.MAXQUANITY]
            ]
        }
            
        if allowed_NTIPAliases[self.current_section]:
            for alias in allowed_NTIPAliases[self.current_section]:
                if isinstance(alias[0], str):
                    if lookup_key == alias[0]:
                        return Token(alias[1], lookup_key)
                elif isinstance(alias[0], dict):
                    if lookup_key in alias[0]:
                        return Token(alias[1], alias[0][lookup_key])

    def _create_d2r_image_data_lookup(self):
        lookup_key = ""
        found_match = re.match(r"(\w+)\s*", self.get_current_iteration_of_text_raw()) # Look at chars until we find a space.

        if found_match and found_match.group(1):
            found = found_match.group(1)
            for i in range(len(found)):
                lookup_key += found[i]
                self._advance()

        # Converts stuff like ethereal to NTIPAliasFlag['ethereal']
        if self.current_section == NipSections.PROP:
            if lookup_key in NTIPAliasClass and self.tokens[-2].type == TokenType.CLASS:
                return Token(TokenType.NTIPAliasClass, lookup_key)
            elif lookup_key in NTIPAliasQuality and self.tokens[-2].type == TokenType.QUALITY:
                return Token(TokenType.NTIPAliasQuality, lookup_key)
            elif lookup_key in NTIPAliasClassID and self.tokens[-2].type == TokenType.NAME:
                return Token(TokenType.NTIPAliasClassID, lookup_key)
            elif lookup_key in NTIPAliasFlag and self.tokens[-2].type == TokenType.FLAG:
                return Token(TokenType.NTIPAliasFlag, lookup_key)
            elif lookup_key in NTIPAliasType and self.tokens[-2].type == TokenType._TYPE:
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
