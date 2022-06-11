from nip.NTIPAliasQuality import NTIPAliasQuality
from nip.NTIPAliasClass import NTIPAliasClass
from nip.NTIPAliasClassID import NTIPAliasClassID
from nip.NTIPAliasFlag import NTIPAliasFlag
from nip.NTIPAliasStat import NTIPAliasStat
from nip.NTIPAliasType import NTIPAliasType

# ! The above imports are necessary, they are used within the eval statements. Your text editor probably is not showing them as not in use.

from dataclasses import dataclass
from nip.lexer import Lexer, NipSyntaxError, NipSections
from nip.tokens import Token, TokenType
from nip.utils import find_unique_or_set_base

class NipSyntaxErrorSection(NipSyntaxError): 
    # TODO CONVERT THIS TO THE OTHER ERROR CLASS IN lexer.py
    
    def __init__(self, token, section):
        super().__init__(f"[ {token.type} ] : {token.value} can not be used in section [ {section} ].")

    def __str__(self):
        return f"[ {self.token_errored_on.type} : {self.token_errored_on.value} ] can not be used in section [ {self.section_errored_on} ]."

@dataclass
class NIPExpression:
    raw: str
    should_id_transpiled: str | None
    transpiled: str
    should_pickup: str | None
    tokens: list[Token]


nip_expressions: list[NIPExpression] = []


token_transpile_map = {

    TokenType.NUMBER: "{}",
    # TokenType.NUMBERPERCENT: "int({})",

    # TokenType.KeywordNTIPAliasIDName: "str(item_data['NTIPAliasIdName']).lower()", # * Special case
    TokenType.KeywordNTIPAliasName: "int(item_data['NTIPAliasClassID'])", # * [name] (NTIPAliasName) is an alias for NTIPAliasClassID
    TokenType.KeywordNTIPAliasClass: "int(item_data['NTIPAliasClass'])", # * This is not ClassID, but Class which refers to normal, expectational, elte
    TokenType.KeywordNTIPAliasQuality: "int(item_data['NTIPAliasQuality'])", 
    # TokenType.KeywordNTIPAliasType: "int(item_data['NTIPAliasType'])", # * Special case
    # TokenType.KeywordNTIPAliasFlag: "int(item_data['NTIPAliasFlag'])", # * Special case

    # TokenType.ValueNTIPAliasFlag: "NTIPAliasFlag['{}']", # * Special case
    TokenType.ValueNTIPAliasType: "int(NTIPAliasType['{}'])",
    TokenType.ValueNTIPAliasClass: "int(NTIPAliasClass['{}'])",
    TokenType.ValueNTIPAliasQuality: "int(NTIPAliasQuality['{}'])",
    TokenType.ValueNTIPAliasClassID: "int(NTIPAliasClassID['{}'])",
    # TokenType.ValueNTIPAliasIDName : "str(NTIPAliasIDName['{}']).lower()", # * Special case
}
def shift(l: list, index: int, value):
    return l[:index] + [value] + l[index+1:]

def transpile(tokens: list[Token], isPickUpPhase: bool = False, transpiled_expressions: str = ""):
    """
        Transpiles the tokens into python code, some of the code that gets transpiled is dependent if we are in the pickup phase or not
    """


    expression = ""
    section_start = True
    section_open_paranthesis_count = 0

    print("tokens", tokens)
    print("detokenize", Lexer().detokenize(tokens))

    for i, token in enumerate(tokens):
        if token == None: continue
        token_value = str(token.value)
        if section_start:
            expression += "("
            section_start = False
            section_open_paranthesis_count += 1
        if token.type in token_transpile_map:
            expression += f"({token_transpile_map[token.type].format(token_value)})"
            continue
        match token.type:
            case TokenType.NE | TokenType.GT | TokenType.LT | TokenType.GE | TokenType.LE:
                if tokens[i + 1].type != TokenType.ValueNTIPAliasFlag:
                    expression += token_value
            case TokenType.EQ:
                if tokens[i + 1].type == TokenType.ValueNTIPAliasFlag: continue
                if isPickUpPhase and tokens[i + 1].type == TokenType.ValueNTIPAliasIDName: continue
                expression += "=="
            case TokenType.OR | TokenType.AND | TokenType.LPAREN | TokenType.RPAREN | TokenType.PLUS | TokenType.MINUS | TokenType.MULTIPLY | TokenType.DIVIDE:
                expression += token_value
                if token.type == TokenType.LPAREN:
                    section_open_paranthesis_count += 1
                elif token.type == TokenType.RPAREN:
                    section_open_paranthesis_count -= 1
            case TokenType.SECTIONAND:
                expression += ")"
                section_open_paranthesis_count -= 1
                expression += "and"
                section_start = True
            case TokenType.ValueNTIPAliasStat:
                expression += f"(int(item_data['NTIPAliasStat'].get('{token_value}', 0)))"
            case TokenType.KeywordNTIPAliasIDName:
                if not isPickUpPhase:
                    expression += "(str(item_data['NTIPAliasIdName']).lower())"
            case TokenType.KeywordNTIPAliasFlag:
                if tokens[i + 2].type == TokenType.ValueNTIPAliasFlag: # * Get the token after the operator
                    condition_type = tokens[i + 1] # * Get the operator
                    flag = NTIPAliasFlag[tokens[i + 2].value] # * I.E if the input is ethereal, flag would be equal to "0x400000" (which is a string)
                    match condition_type.type:
                        case TokenType.EQ:
                            expression += f"(item_data['NTIPAliasFlag']['{flag}'])"
                        case TokenType.NE:
                            expression += f"(not item_data['NTIPAliasFlag']['{flag}'])"
            case TokenType.ValueNTIPAliasIDName:
                if tokens[i - 2].type == TokenType.KeywordNTIPAliasIDName:
                    if isPickUpPhase:
                        base, quality = find_unique_or_set_base(token_value)
                        expression += f"(int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['{base}']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['{quality}']))"
                    else:
                        expression += f"(str('{token_value}').lower())"
                else:
                    expression += "(0)"
            case TokenType.KeywordNTIPAliasType:
                token_after_operator = tokens[i + 2]
                # * The below code uses short-circuit evaluation
                expression += f"(int(NTIPAliasType['{token_after_operator.value}']) in item_data['NTIPAliasType'] and int(NTIPAliasType['{token_after_operator.value}']) or -1)"
            case TokenType.UNKNOWN: # * _ is default..
                expression += "(0)"

    for _ in range(section_open_paranthesis_count): # * This is needed to close the last section
        expression += ")"
    return expression
                        
# TODO don't forget to remove this when done with it
"""def transpile(tokens, isPickUpPhase=False):
#     print(tokens)
#     expression = ""
#     section_start = True
#     for i, token in enumerate(tokens):
#         if section_start:
#             expression += "("
#             section_start = False
#         if token.type == TokenType.ValueNTIPAliasStat:
#             if len(tokens) >= i + 2 and tokens[i + 2].type == TokenType.NUMBERPERCENT: # Look at the other side of the comparsion.
#                 expression += f"(int(-1))" # Ignore it since it wasn't a dict and the user tried to use a %
#                 # Write an expression to test make sure the item_data['Item']['NTIPAliasStatProps'] is a dict.
#                 # stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
#                 # stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"
#                 # is_dict = eval(f"isinstance({stat_min_max}, dict)") # ghetto, but for now, ok..
#                 # if is_dict:
#                     # expression += f"(int(({stat_value} - {stat_min_max}['min']) * 100.0 / ({stat_min_max}['max'] - {stat_min_max}['min'])))"
#                 # else:
#             else:
#                 expression += f"(int(item_data['NTIPAliasStat'].get('{token.value}', -1)))"
#                 # expression += _create_nip_value_string(token.value)
#                 # stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
#                 # stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"
#                 # clamp value between min and max
#                 # expression += f"(({stat_value} >= {stat_min_max}['max'] and {stat_min_max}['max']) or ({stat_value} <= {stat_min_max}['min'] and {stat_min_max}['min']) or {stat_value})"
#                 # expression += f"(int(item_data['NTIPAliasStat']['{token.value}']))"

#         elif token.type == TokenType.ValueNTIPAliasFlag:
#             pass
#             # we don't need the flag value here, it's used below
#             # expression += f"NTIPAliasFlag['{token.value}']"
#         elif (token.type == TokenType.ValueNTIPAliasType or
#              token.type == TokenType.ValueNTIPAliasClass or
#              token.type == TokenType.ValueNTIPAliasQuality or
#              token.type == TokenType.ValueNTIPAliasClassID):
#             token_data = token.data()
#             expression += _create_nip_value_string(token_data["type"], token_data["value"])
#         elif (
#             token.type == TokenType.KeywordNTIPAliasName or
#             token.type == TokenType.KeywordNTIPAliasClass or
#             token.type == TokenType.KeywordNTIPAliasQuality
#         ):
#             token_data = token.data()
#             expression += _create_nip_keyword_string(token_data["type"].replace("Keyword", ""))
#         elif token.type == TokenType.KeywordNTIPAliasIDName:
#             if not isPickUpPhase:
#                 expression += "(str(item_data['NTIPAliasIdName']).lower())"
#         elif token.type == TokenType.KeywordNTIPAliasFlag:
#             if tokens[i + 2].type == TokenType.ValueNTIPAliasFlag:
#                 condition_type = tokens[i + 1]
#                 if condition_type.type == TokenType.EQ:
#                     expression += f"(item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
#                 elif condition_type.type == TokenType.NE:
#                     expression += f"(not item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
#             # Check if the flag we're looking for (i.e ethereal) is i + 2 away from here, if it is, grab it's value (0x400000) and place it inside the lookup.
#         elif token.type == TokenType.KeywordNTIPAliasType:
#             next_type = tokens[i + 2] # The type we're looking for
#             expression += f"(int(NTIPAliasType['{next_type.value}']) in item_data['NTIPAliasType'] and int(NTIPAliasType['{next_type.value}']) or -1)"
#         elif token.type == TokenType.EQ:
#             if tokens[i + 1].type != TokenType.ValueNTIPAliasFlag:
#                 if not isPickUpPhase:
#                     expression += "=="
#                 else:
#                     if not tokens[i - 1].type == TokenType.KeywordNTIPAliasIDName:
#                         expression += "=="
#         elif token.type in [TokenType.NE, TokenType.GT, TokenType.LT, TokenType.GE, TokenType.LE]:
#             if tokens[i + 1].type != TokenType.ValueNTIPAliasFlag:
#                 expression += token.value
#         elif token.type == TokenType.NUMBER:
#             expression += f"({token.value})"
#         elif token.type == TokenType.NUMBERPERCENT:
#             expression += f"int({token.value})"
#         elif token.type == TokenType.AND:
#             if tokens[i - 1].type != TokenType.AND:
#                 expression += "and"
#         elif token.type == TokenType.SECTIONAND:
#             if tokens[i - 1].type != TokenType.SECTIONAND:
#                 expression += ")"
#                 expression += "and"
#                 section_start = True
#         elif token.type == TokenType.UNKNOWN:
#             if tokens[i - 2].type == TokenType.KeywordNTIPAliasIDName:
#                 if isPickUpPhase:
#                     base, quality = find_unique_or_set_base(token.value)
#                     expression += f"(int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['{base}']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['{quality}']))"
#                 else:
#                     expression += f"(str('{token.value}').lower())"
#             else:
#                 expression += "(-1)"
#         else:
#             expression += f"{token.value}"
#         expression += "" # add space if spaces are needed
#     expression += ")" # * Close the last bracket since there is no other section and to close it.
#     return expression
"""


def validate_correct_math_syntax(left_token=None, right_token=None):
    """Makes sure that there are no invalid math operations going on inside the expression"""
    allowed_left_and_right_tokens = [
        TokenType.ValueNTIPAliasClass,
        TokenType.ValueNTIPAliasClassID,
        TokenType.ValueNTIPAliasFlag,
        TokenType.ValueNTIPAliasType,
        TokenType.ValueNTIPAliasQuality,
        TokenType.ValueNTIPAliasStat,
        
        TokenType.KeywordNTIPAliasClass,
        TokenType.KeywordNTIPAliasFlag,
        TokenType.KeywordNTIPAliasType,
        TokenType.KeywordNTIPAliasQuality,
        TokenType.KeywordNTIPAliasName,
        TokenType.KeywordNTIPAliasIDName,
        TokenType.KeywordNTIPAliasMaxQuantity,

        TokenType.NUMBER,
    ]
    if left_token and left_token.type not in allowed_left_and_right_tokens:
        raise NipSyntaxError("NIP_0x6", "unexpected token on left of math operator")
    if right_token and right_token.type not in allowed_left_and_right_tokens:
        raise NipSyntaxError("NIP_0x7", "unexpected token on right of math operator")

OPENING_PARENTHESIS_COUNT = 0
def validate_correct_parenthesis_syntax(current_pos, all_tokens, left_token=None, right_token=None):
    """Makes sure that every parenthesis is closed and that there are no unclosed parenthesis."""
    global OPENING_PARENTHESIS_COUNT

    token = all_tokens[current_pos]

    if token.type == TokenType.LPAREN:
        OPENING_PARENTHESIS_COUNT += 1
    elif token.type == TokenType.RPAREN:
        OPENING_PARENTHESIS_COUNT -= 1
       
        # * Backtrace until the last opening to make sure it wasn't from the past section.
        for i in range(current_pos, -1, -1):
            # print(all_tokens[i].type)
            if all_tokens[i].type == TokenType.SECTIONAND:
                raise NipSyntaxError("NIP_0x8", "parenthesis cannot cross the section and (#)")
    
    if current_pos == len(all_tokens) - 1:
        if OPENING_PARENTHESIS_COUNT != 0:
            # OPENING_PARENTHESIS_COUNT = 0
            if OPENING_PARENTHESIS_COUNT > 0:
                OPENING_PARENTHESIS_COUNT = 0
                raise NipSyntaxError("NIP_0x8", "unclosed parenthesis")
            else:
                OPENING_PARENTHESIS_COUNT = 0
                raise NipSyntaxError("NIP_0x9", "unopened parenthesis")
        OPENING_PARENTHESIS_COUNT = 0
        
def validate_digits_syntax(left=None, right=None):
    """Makes sure that the left and right tokens are valid to be next to a digit."""
    allowed_left_and_right_tokens = [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.MULTIPLY,
        TokenType.DIVIDE,
        TokenType.MODULO,
        TokenType.POW,
        
        TokenType.AND,
        TokenType.OR,
        TokenType.EQ,
        TokenType.NE,
        TokenType.GT,
        TokenType.LT,
        TokenType.GE,
        TokenType.LE,

        TokenType.SECTIONAND,

        TokenType.LPAREN,
        TokenType.RPAREN,

    ]

    if left:
        if left.type not in allowed_left_and_right_tokens:
            raise NipSyntaxError("NIP_0x10", "Expected operator on left of number")
    if right:
        if right.type not in allowed_left_and_right_tokens:
            raise NipSyntaxError("NIP_0x11", "Expected operator on right of number")
    

def validate_logical_operators(left=None, right=None):
    """Makes sure that the logical operators are used correctly."""
    allowed_left_and_right_tokens = [
        TokenType.NUMBER,

        TokenType.ValueNTIPAliasClass,
        TokenType.ValueNTIPAliasClassID,
        TokenType.ValueNTIPAliasFlag,
        TokenType.ValueNTIPAliasType,
        TokenType.ValueNTIPAliasQuality,
        TokenType.ValueNTIPAliasStat,
        
        TokenType.KeywordNTIPAliasClass,
        TokenType.KeywordNTIPAliasFlag,
        TokenType.KeywordNTIPAliasType,
        TokenType.KeywordNTIPAliasQuality,
        TokenType.KeywordNTIPAliasName,
        TokenType.KeywordNTIPAliasIDName,
        TokenType.KeywordNTIPAliasMaxQuantity,

    ]
    if left:
        if left.type not in allowed_left_and_right_tokens + [TokenType.RPAREN]:
            raise NipSyntaxError("NIP_0x12", "Expected token on left of logical operator")
    if right:
        if right.type not in allowed_left_and_right_tokens + [TokenType.LPAREN]:
            raise NipSyntaxError("NIP_0x13", "Expected token on right of logical operator")
    else:
        raise NipSyntaxError("NIP_0x14", "Expected token on right of logical operator")


def validate_nip_expression_syntax(nip_expression): # * enforces that {property} # {stats} # {maxquantity}
    tokens = None

    if not nip_expression:
        return

    all_tokens = []

    split_nip_expression = nip_expression.split("#")
    split_nip_expression_len = len(split_nip_expression)

    if split_nip_expression_len >= 1 and split_nip_expression[0]: # property
        tokens = Lexer().create_tokens(split_nip_expression[0], NipSections.PROP)
        all_tokens.extend(tokens)
        for token in tokens:
            if token.type == TokenType.ValueNTIPAliasStat:
                raise NipSyntaxErrorSection(token, "property")
    if split_nip_expression_len >= 2 and split_nip_expression[1]: # stats
        tokens = Lexer().create_tokens(split_nip_expression[1], NipSections.STAT)
        all_tokens.extend(tokens)
        for token in tokens:
            is_invalid_stat_lookup = (
                token.type == TokenType.ValueNTIPAliasClass or
                token.type == TokenType.ValueNTIPAliasClassID and token.value != '523' or # 523 refers to gold
                token.type == TokenType.ValueNTIPAliasFlag or
                token.type == TokenType.ValueNTIPAliasType or
                token.type == TokenType.ValueNTIPAliasQuality
            )

            if is_invalid_stat_lookup:
                raise NipSyntaxErrorSection(token, "stats")

    if split_nip_expression_len >= 3 and split_nip_expression[2]: # maxquantity
        tokens = Lexer().create_tokens(split_nip_expression[2], NipSections.MAXQUANTITY)
        all_tokens.extend(tokens)
        for token in tokens:
            is_invalid_maxquantity_lookup = (
                token.type == TokenType.ValueNTIPAliasClass or
                token.type == TokenType.ValueNTIPAliasQuality or
                token.type == TokenType.ValueNTIPAliasClassID or
                token.type == TokenType.ValueNTIPAliasFlag or
                token.type == TokenType.ValueNTIPAliasType or
                token.type == TokenType.ValueNTIPAliasStat
            )

            if is_invalid_maxquantity_lookup:
                raise NipSyntaxErrorSection(token, "maxquantity")

    # * Further syntax validation
    math_tokens = [TokenType.MULTIPLY, TokenType.PLUS, TokenType.MINUS, TokenType.DIVIDE, TokenType.MODULO, TokenType.POW]
    logical_tokens = [TokenType.AND, TokenType.OR, TokenType.EQ, TokenType.NE, TokenType.GT, TokenType.LT, TokenType.GE, TokenType.LE]

    for i, token in enumerate(all_tokens):
        # Get the left and right tokens for the current token
        left = None
        right = None
        if i > 0:
            left = all_tokens[i-1]
        if i < len(all_tokens)-1:
            right = all_tokens[i+1]

        if token.type == TokenType.LPAREN or token.type == TokenType.RPAREN or i == len(all_tokens) - 1: # * Also check the last token no matter what so if there is an opening parenthesis without a closing parenthesis it will raise an error
            validate_correct_parenthesis_syntax(i, all_tokens, left_token=left, right_token=right)
        elif token.type == TokenType.EQ:
            if i == len(all_tokens) - 1: # * Check to make sure the next token is a token. 
                # ! the logic only makes sense for the last token, what the fuck
                raise NipSyntaxError("NIP_0x15", "No value after equal sign")
        elif token.type in math_tokens:
            validate_correct_math_syntax(left_token=left, right_token=right)
        # * Make sure two numbers aren't next to each other.
        elif token.type == TokenType.NUMBER or token.type == TokenType.UNKNOWN:
            validate_digits_syntax(left=left, right=right)
        elif token.type in logical_tokens:
            validate_logical_operators(left=left, right=right)
    
    return True


def remove_quantity(expression): # ! This is a bit ghetto, but since we're not using the maxquantity, we can just remove it. # 
    # TODO FIX THIS SHIT
    split_expression = expression.split("#")
    if len(split_expression) == 3:
        split_expression = (split_expression[0] + "#" + split_expression[1]).split("#")
        if len(split_expression[1]) <= 1:
            return split_expression[0]
        else:
            return "#".join(split_expression)
    return expression


def get_section_from_tokens(all_tokens: list[Token], section: NipSections | None = None) -> dict[NipSections, list[Token]]:
    tokens_split_by_section = []
    temp_section = []

    for i, token in enumerate(all_tokens):
        if token.type == TokenType.SECTIONAND:
            tokens_split_by_section.append(temp_section)
            temp_section = []
        elif i == len(all_tokens) - 1:
            temp_section.append(token)
            tokens_split_by_section.append(temp_section)
            temp_section = []
        else:
            temp_section.append(token)
    section_tokens_len = len(tokens_split_by_section)

    nip_map = {
            NipSections.PROP: tokens_split_by_section[0] if section_tokens_len >= 1 else [],
            NipSections.STAT: tokens_split_by_section[1] if section_tokens_len >= 2 else [],
            NipSections.MAXQUANTITY: tokens_split_by_section[2] if section_tokens_len >= 3 else []
        }

    return nip_map


def prepare_nip_expression(expression: str) -> str:
    if not expression.startswith("//") and not expression.startswith("-"):
        expression = expression.lower()
        expression = expression.replace("'", "")
        expression = expression.split("//")[0] # * Ignore the comments inside the nip expression
        expression = remove_quantity(expression)
        if validate_nip_expression_syntax(expression):
            return expression
    return ''


def transpile_nip_expression(expression: str | list[Token], isPickUpPhase=False):
    if isinstance(expression, str):
        expression = prepare_nip_expression(expression)
        if expression:
            tokens = Lexer().create_tokens(expression)
            transpiled_expression = transpile(tokens, isPickUpPhase=isPickUpPhase)
            if transpiled_expression:
                return transpiled_expression
    elif isinstance(expression, list):
        transpiled_expression = transpile(expression, isPickUpPhase=isPickUpPhase)
        if transpiled_expression:
            return transpiled_expression

def load_nip_expression(nip_expression):
    nip_expression = prepare_nip_expression(nip_expression)

    if not nip_expression: return

    tokens = Lexer().create_tokens(nip_expression)
    transpiled_expression = transpile_nip_expression(tokens)
    split_tokens = get_section_from_tokens(tokens)
    if transpiled_expression:
        nip_expressions.append(
            NIPExpression(
                raw=nip_expression,
                tokens=tokens,
                transpiled=transpiled_expression,
                should_id_transpiled=transpile_nip_expression(split_tokens[NipSections.PROP]),
                should_pickup=transpile_nip_expression(split_tokens[NipSections.PROP], isPickUpPhase=True) # * Some stuff gets transpiled differently in the pickup phase
            )
        )
        

