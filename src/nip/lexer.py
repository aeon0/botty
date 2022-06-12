from dataclasses import dataclass
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
from colorama import init, Fore
from rapidfuzz.string_metric import levenshtein


init()

WHITESPACE = " \t\n\r\v\f"
DIGITS = "0123456789.-" # ! Put % back in here when ready to use percentages.
SYMBOLS = [">", "=> ", "<", "<=", "=", "!", "", "", ",", "&", "|", "#", "/"]
MATH_SYMBOLS = ["(", ")", "^", "*", "/", "\\", "+", "-"]
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'"


class NipSections(Enum):
    PROP = 1
    STAT = 2
    MAXQUANTITY = 3


class NipSyntaxError(Exception):
    def __init__(self, ecode: str|int = 0, message: str = '', expression: str = ''):
        self.message = message
        self.type = type
        self.ecode = ecode
        self.expression = expression

    def __str__(self):
        return f"{Fore.RED}{self.ecode}:{Fore.CYAN}{self.message}:{Fore.YELLOW}{self.expression.strip()}{Fore.WHITE}"


class Lexer:
    def __init__(self):
        self.current_section: NipSections = NipSections.PROP
        self.current_token: str | None = ""
        self.text_i: int = -1
        self.tokens: List[Token] = []


    def increment_section(self):
        if self.current_section == NipSections.PROP:
            self.current_section = NipSections.STAT
        elif self.current_section == NipSections.STAT:
            self.current_section = NipSections.MAXQUANTITY


    def get_text(self):
        return "".join(self.text)


    def get_current_iteration_of_text_raw(self):
        """
            Returns the self.text in a string type, and at its current iteration.
        """
        return self.get_text()[self.text_i:]

    def _advance(self):
        try:
            self.text_i += 1
            self.current_token = self.text[self.text_i]
        except IndexError:
            self.current_token = None


    def create_tokens(self, nip_expression: str, starting_section: NipSections = NipSections.PROP):
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
            elif self.current_token == "[":
                self.tokens.append(self._create_keyword_lookup())
            elif self.current_token in CHARS:
                self.tokens.append(self._create_d2r_image_data_lookup())
            else:
                raise NipSyntaxError("NIP_0x1", "Unknown token: " + self.current_token, self.get_text())
        return self.tokens

    def detokenize(self, tokens: List[Token]) -> str:
        """ Detokenizes a list of tokens. """
        token_to_value = {
            TokenType.NUMBER: '{}',
            TokenType.NUMBERPERCENT: '{}%',
            TokenType.PLUS: '+',
            TokenType.MINUS: '-',
            TokenType.MULTIPLY: '*',
            TokenType.DIVIDE: '/',
            TokenType.MODULO: '%',

            TokenType.LPAREN: '(',
            TokenType.RPAREN: ')',

            TokenType.GT: '>',
            TokenType.LT: '<',
            TokenType.LE: '<=',
            TokenType.GE: '>=',
            TokenType.EQ: '==',
            TokenType.NE: '!=',

            TokenType.AND: '&&',
            TokenType.OR: '||',

            TokenType.SECTIONAND: '#',

            TokenType.KeywordNTIPAliasIDName: '[idname]',
            TokenType.KeywordNTIPAliasName: '[name]',
            TokenType.KeywordNTIPAliasFlag: '[flag]',
            TokenType.KeywordNTIPAliasQuality: '[quality]',
            TokenType.KeywordNTIPAliasClass: '[class]',
            TokenType.KeywordNTIPAliasMaxQuantity: '[maxquantity]',
            TokenType.KeywordNTIPAliasType: '[type]',

            TokenType.ValueNTIPAliasIDName: '{}',
            TokenType.ValueNTIPAliasClass: '{}',
            TokenType.ValueNTIPAliasClassID: '{}',
            TokenType.ValueNTIPAliasFlag: '{}',
            TokenType.ValueNTIPAliasQuality: '{}',
            TokenType.ValueNTIPAliasStat: '{}',
            TokenType.ValueNTIPAliasType: '{}',
            TokenType.ValueNTIPAlias: '{}',
        }

        expression = ''

        # * Find NTIPAliasStat key by value.
        def find_stat_by_value(wanted_value):
            for key, value in NTIPAliasStat.items():
                if value == wanted_value:
                    return key
            return None

        for token in tokens:
            if token.type in token_to_value:
                if token.type == TokenType.ValueNTIPAliasStat:
                    expression += token_to_value[token.type].format(f'[{find_stat_by_value(token.value)}]')               
                else:
                    expression += token_to_value[token.type].format(token.value)                  
            expression += ' '
        return expression.strip()
            
                

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

    def _create_digits(self) -> Token:
        found_decimal_number = re.match(r"^-*[0-9]+\.[0-9]+", self.get_current_iteration_of_text_raw())
        if found_decimal_number:
            return self._create_custom_digit_token(found_decimal_number.group(0))

        shorthand_decimal_number = re.match(r"^-*\.[0-9]+", self.get_current_iteration_of_text_raw())
        if shorthand_decimal_number:
            return self._create_custom_digit_token(shorthand_decimal_number.group(0), "0", append_front=True)

        found_whole_number = re.match(r"^-*[0-9]+", self.get_current_iteration_of_text_raw())
        if found_whole_number:
            return self._create_custom_digit_token(found_whole_number.group(0))
        return Token(TokenType.UNKNOWN, self.current_token)


    def _create_math_operator(self):
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

        symbol = self.current_token

        if symbol in symbol_map:
            return Token(symbol_map[symbol], symbol)
        
        return Token(TokenType.UNKNOWN, symbol)

    def _create_keyword_lookup(self) -> Token:
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
            else:
                raise NipSyntaxError("NIP_0x2", "Missing ] after keyword", self.get_text())
        if lookup_key:
            if self.current_section == NipSections.PROP:
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
                    Logger.warning(f"Unknown property lookup: \"{lookup_key}\" {''.join(self.text)}  {self.current_section}")
                    
                    return Token(TokenType.UNKNOWN, lookup_key)
            elif self.current_section == NipSections.STAT:
                if lookup_key in NTIPAliasStat:
                    return Token(TokenType.ValueNTIPAliasStat, NTIPAliasStat[lookup_key])
                else:
                    # spell_check = ""
                    # for key in NTIPAliasStat:
                    #     if levenshtein(lookup_key, key) < 3:
                    #         spell_check = f", did you mean {key}?"
                    # raise NipSyntaxError("NIP_0x3", f"Unknown NTIPStat lookup: {lookup_key}{spell_check}", self.get_text())
                    return Token(TokenType.UNKNOWN, lookup_key)
            elif self.current_section == NipSections.MAXQUANTITY:
                pass
        
            return Token(TokenType.UNKNOWN, lookup_key)

    def _create_d2r_image_data_lookup(self) -> Token:
        lookup_key = ""
        
        found_lookup_key = re.match(r"^(\w+)\s*", self.get_current_iteration_of_text_raw())
        # print(found_lookup_key, self.get_current_iteration_of_text_raw())
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
            elif self.tokens[-2].type == TokenType.KeywordNTIPAliasIDName:
                return Token(TokenType.ValueNTIPAliasIDName, lookup_key)
                # if self.tokens[-2].type != TokenType.KeywordNTIPAliasIDName: # * Make sure the last token isn't [idname]
                #     # Add all the NTIPAlias* to a dict
                #     NTIPAliasAll = NTIPAliasClass | NTIPAliasQuality | NTIPAliasClassID | NTIPAliasFlag | NTIPAliasType
                #     for key in NTIPAliasAll:
                #         if levenshtein(lookup_key, key) < 3:
                #             raise NipSyntaxError( "NIP_0x4", f"Unknown NTIP lookup: {lookup_key} did you mean {key}?", self.get_text())
                # else:
                #     return Token(TokenType.ValueNTIPAliasIDName, lookup_key)
                
                return Token(TokenType.UNKNOWN, lookup_key)
        elif self.current_section == NipSections.STAT:
            if lookup_key in NTIPAliasStat:
                return Token(TokenType.ValueNTIPAliasStat, lookup_key)
            else:
                return Token(TokenType.UNKNOWN, lookup_key)
        return Token(TokenType.UNKNOWN, lookup_key)

    def _create_logical_operator(self) -> Token:
        char = self.current_token
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

        found = re.match(pattern, self.get_current_iteration_of_text_raw())
        if found:
            found_text = found.group(1)
            if logical_operator_map[found_text] == TokenType.SECTIONAND:
                self.increment_section()
            for _ in range(len(found_text)):
                self._advance()
            
            pythonic_operator = found_text.replace("#", "and").replace("||", "or").replace("&&", "and")
            return Token(logical_operator_map[found_text], pythonic_operator)
        else:
            raise NipSyntaxError("NIP_0x5, "f"Invalid logical operator: '{char}'", self.get_text())
