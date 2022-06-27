from bnip.NTIPAliasQuality import NTIPAliasQuality
from bnip.NTIPAliasClass import NTIPAliasClass
from bnip.NTIPAliasClassID import NTIPAliasClassID
from bnip.NTIPAliasFlag import NTIPAliasFlag
from bnip.NTIPAliasStat import NTIPAliasStat
from bnip.NTIPAliasType import NTIPAliasType

# ! The above imports are necessary, they are used within the eval statements. Your text editor probably is not showing them as not in use.

from dataclasses import dataclass
from bnip.lexer import Lexer, BNipSections
from bnip.BNipExceptions import BNipSyntaxError
from bnip.tokens import Token, TokenType
from bnip.utils import find_unique_or_set_base

@dataclass
class BNIPExpression:
    raw: str
    should_id_transpiled: str | None
    transpiled: str
    should_pickup: str | None
    tokens: list[Token]


bnip_expressions: list[BNIPExpression] = []


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

def transpile(tokens: list[Token], isPickUpPhase: bool = False, transpiled_expressions: str = ""):
    """
        Transpiles the tokens into python code, some of the code that gets transpiled is dependent if we are in the pickup phase or not
    """


    expression = ""
    section_start = True
    section_open_paranthesis_count = 0

    # print("tokens", tokens)
    # print("detokenize", Lexer().detokenize(tokens))

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
                if tokens[i + 1].type == TokenType.ValueNTIPAliasFlag: 
                    continue
                if isPickUpPhase and tokens[i + 1].type == TokenType.ValueNTIPAliasIDName: 
                    continue
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
            case TokenType.KeywordNTIPAliasStat:
                expression += "(int(item_data.get('NTIPAliasStat', {})" + f".get('{token_value}', 0)))"
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


def validate_correct_math_syntax(left_token=None, right_token=None):
    """Makes sure that there are no invalid math operations going on inside the expression"""
    allowed_left_and_right_tokens = [
        TokenType.KeywordNTIPAliasClass,
        TokenType.KeywordNTIPAliasFlag,
        TokenType.KeywordNTIPAliasMaxQuantity,
        TokenType.KeywordNTIPAliasName,
        TokenType.KeywordNTIPAliasQuality,
        TokenType.KeywordNTIPAliasType,
        TokenType.KeywordNTIPAliasStat,

        TokenType.ValueNTIPAliasClass,
        TokenType.ValueNTIPAliasClassID,
        TokenType.ValueNTIPAliasFlag,
        TokenType.ValueNTIPAliasQuality,
        TokenType.ValueNTIPAliasStat,
        TokenType.ValueNTIPAliasType,

        TokenType.NUMBER,

        TokenType.LPAREN,
        TokenType.RPAREN,
    ]
    if left_token and left_token.type not in allowed_left_and_right_tokens:
        raise BNipSyntaxError2("BNIP_0x3", "unexpected token on left of math operator")
    if right_token and right_token.type not in allowed_left_and_right_tokens:
        raise BNipSyntaxError2("BNIP_0x4", "unexpected token on right of math operator")

OPENING_PARENTHESIS_COUNT = 0 # * This needs to be reset every time an validation error occurs
CURRENT_EXPRESSION = ""
def BNipSyntaxError2(error_code, error_message): # * "hook" the error constructor so every time the error is raised / called, we reset the opening parenthesis count
    global OPENING_PARENTHESIS_COUNT
    OPENING_PARENTHESIS_COUNT = 0
    print(CURRENT_EXPRESSION)
    return BNipSyntaxError(error_code, error_message, CURRENT_EXPRESSION)


def validate_correct_parenthesis_syntax(current_pos, all_tokens, left_token=None, right_token=None):
    """Makes sure that every parenthesis is closed and that there are no unclosed parenthesis."""


    allowed_left_and_right_tokens = [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.MULTIPLY,
        TokenType.DIVIDE,
        TokenType.EQ,
        TokenType.NE,
        TokenType.GT,
        TokenType.LT,
        TokenType.GE,
        TokenType.LE,
        TokenType.OR,
        TokenType.AND,
        TokenType.SECTIONAND,
        TokenType.NOTIFICATION
    ]

    global OPENING_PARENTHESIS_COUNT
    token = all_tokens[current_pos]
    if token.type == TokenType.LPAREN:
        OPENING_PARENTHESIS_COUNT += 1
        if left_token and left_token.type not in allowed_left_and_right_tokens + [TokenType.LPAREN]:
            raise BNipSyntaxError2("BNIP_0x18", "unexpected token on left of parenthesis")
    elif token.type == TokenType.RPAREN:
        if right_token and right_token.type not in allowed_left_and_right_tokens + [TokenType.RPAREN]:
            raise BNipSyntaxError2("BNIP_0x19", "unexpected token on right of parenthesis")
        OPENING_PARENTHESIS_COUNT -= 1




        # TODO Backtrace until the last opening to make sure it wasn't from the past section.
        # for i in range(current_pos, -1, -1):
        #     # print(all_tokens[i].type)
        #     if all_tokens[i].type == TokenType.SECTIONAND:
        #         raise BNipSyntaxError2("BNIP_0x8", "parenthesis cannot cross the section and (#)")

    if current_pos == len(all_tokens) - 1:
        if OPENING_PARENTHESIS_COUNT != 0:
            if OPENING_PARENTHESIS_COUNT > 0:
                OPENING_PARENTHESIS_COUNT = 0
                raise BNipSyntaxError2("BNIP_0x6", "unclosed parenthesis")
            else:
                OPENING_PARENTHESIS_COUNT = 0
                raise BNipSyntaxError2("BNIP_0x7", "unopened parenthesis")
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
            raise BNipSyntaxError2("BNIP_0x8", "Expected operator on left of number")
    if right:
        if right.type not in allowed_left_and_right_tokens:
            raise BNipSyntaxError2("BNIP_0x9", "Expected operator on right of number")


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
        TokenType.ValueNTIPAliasIDName,

        TokenType.KeywordNTIPAliasClass,
        TokenType.KeywordNTIPAliasFlag,
        TokenType.KeywordNTIPAliasType,
        TokenType.KeywordNTIPAliasQuality,
        TokenType.KeywordNTIPAliasName,
        TokenType.KeywordNTIPAliasIDName,
        TokenType.KeywordNTIPAliasMaxQuantity,
        TokenType.KeywordNTIPAliasStat
    ]

    if left:
        if left.type not in allowed_left_and_right_tokens + [TokenType.RPAREN]:
            raise BNipSyntaxError2("BNIP_0x10", "Expected token on left of logical operator")
    if right:
        if right.type not in allowed_left_and_right_tokens + [TokenType.LPAREN]:
            raise BNipSyntaxError2("BNIP_0x11", "Expected token on right of logical operator")
    else:
        raise BNipSyntaxError2("BNIP_0x12", "Expected token on right of logical operator")


def validate_bnip_expression_syntax(bnip_expression): # * enforces that {property} # {stats} # {maxquantity}
    tokens = None
    global CURRENT_EXPRESSION
    if not bnip_expression:
        return

    all_tokens = []
    CURRENT_EXPRESSION = bnip_expression

    split_bnip_expression = bnip_expression.split("#")
    split_bnip_expression_len = len(split_bnip_expression)
    if split_bnip_expression_len >= 1: # property
        tokens = Lexer().create_tokens(split_bnip_expression[0], BNipSections.PROP)
        all_tokens.extend(tokens)
        for token in tokens:
            if token.type == TokenType.ValueNTIPAliasStat or token.type == TokenType.UNKNOWN:
                raise BNipSyntaxError2("BNIP_0x13", f"Invalid token '{token.value}' in property section")
    if split_bnip_expression_len >= 2: # stats
        all_tokens.append(Token(TokenType.SECTIONAND, "#"))
        tokens = Lexer().create_tokens(split_bnip_expression[1], BNipSections.STAT)
        all_tokens.extend(tokens)
        for token in tokens:
            is_invalid_stat_lookup = (
                token.type == TokenType.ValueNTIPAliasClass or
                token.type == TokenType.ValueNTIPAliasClassID and token.value != '523' or # 523 refers to gold
                token.type == TokenType.ValueNTIPAliasFlag or
                token.type == TokenType.ValueNTIPAliasType or
                token.type == TokenType.ValueNTIPAliasQuality or
                token.type == TokenType.UNKNOWN
            )

            if is_invalid_stat_lookup:
                raise BNipSyntaxError2("BNIP_0x14", f"Invalid token '{token.value}' in stats section")

    if split_bnip_expression_len >= 3: # maxquantity
        # all_tokens.append(Token(TokenType.SECTIONAND, "#"))
        tokens = Lexer().create_tokens(split_bnip_expression[2], BNipSections.MAXQUANTITY)
        all_tokens.extend(tokens)
        for token in tokens:
            is_invalid_maxquantity_lookup = (
                token.type == TokenType.ValueNTIPAliasClass or
                token.type == TokenType.ValueNTIPAliasQuality or
                token.type == TokenType.ValueNTIPAliasClassID or
                token.type == TokenType.ValueNTIPAliasFlag or
                token.type == TokenType.ValueNTIPAliasType or
                token.type == TokenType.ValueNTIPAliasStat or
                token.type == TokenType.UNKNOWN
            )

            if is_invalid_maxquantity_lookup:
                pass
                raise BNipSyntaxError2("BNIP_0x15", "Invalid maxquantity lookup")

    # * Further syntax validation
    # print(all_tokens)
    if all_tokens[-1].type == TokenType.SECTIONAND:
        raise BNipSyntaxError2("BNIP_0x16", "unexpected sectionand (#) at end of expression")
    math_tokens = [TokenType.MULTIPLY, TokenType.PLUS, TokenType.MINUS, TokenType.DIVIDE, TokenType.MODULO, TokenType.POW]
    logical_tokens = [TokenType.AND, TokenType.OR, TokenType.EQ, TokenType.NE, TokenType.GT, TokenType.LT, TokenType.GE, TokenType.LE, TokenType.SECTIONAND]
    for i, token in enumerate(all_tokens):
        # Get the left and right tokens for the current token
        left = None
        right = None
        if i > 0:
            left = all_tokens[i-1]
        if i < len(all_tokens)-1:
            right = all_tokens[i+1]
       
        if token.type == TokenType.EQ:
            if i == len(all_tokens) - 1: # * Check to make sure the next token is a token.
                # ! the logic only makes sense for the last token, what the f*ck
                raise BNipSyntaxError2("BNIP_0x17", "No value after equal sign")
        elif token.type in math_tokens:
            validate_correct_math_syntax(left_token=left, right_token=right)
        # * Make sure two numbers aren't next to each other.
        elif token.type == TokenType.NUMBER or token.type == TokenType.UNKNOWN:
            validate_digits_syntax(left=left, right=right)
        
        if token.type in logical_tokens:
            validate_logical_operators(left=left, right=right)

        if token.type == TokenType.LPAREN or token.type == TokenType.RPAREN or i == len(all_tokens) - 1: # * Also check the last token no matter what so if there is an opening parenthesis without a closing parenthesis it will raise an error
            validate_correct_parenthesis_syntax(i, all_tokens, left_token=left, right_token=right)
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


def get_section_from_tokens(all_tokens: list[Token], section: BNipSections | None = None) -> dict[BNipSections, list[Token]]:
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

    bnip_map = {
            BNipSections.PROP: tokens_split_by_section[0] if section_tokens_len >= 1 else [],
            BNipSections.STAT: tokens_split_by_section[1] if section_tokens_len >= 2 else [],
            BNipSections.MAXQUANTITY: tokens_split_by_section[2] if section_tokens_len >= 3 else []
        }

    return bnip_map


def prepare_bnip_expression(expression: str) -> str:
    if not expression.startswith("//") and not expression.startswith("-"):
        expression = expression.lower()
        expression = expression.replace("'", "")
        expression = expression.split("//")[0] # * Ignore the comments inside the nip expression
        expression = remove_quantity(expression)
        if validate_bnip_expression_syntax(expression):
            return expression
    return ''


def transpile_bnip_expression(expression: str | list[Token], isPickUpPhase=False):
    if isinstance(expression, str):
        expression = prepare_bnip_expression(expression)
        if expression:
            tokens = Lexer().create_tokens(expression)
            transpiled_expression = transpile(tokens, isPickUpPhase=isPickUpPhase)
            if transpiled_expression:
                return transpiled_expression
    elif isinstance(expression, list):
        transpiled_expression = transpile(expression, isPickUpPhase=isPickUpPhase)
        if transpiled_expression:
            return transpiled_expression

def generate_expression_object(bnip_expression: str) -> BNIPExpression | None:
    bnip_expression = prepare_bnip_expression(bnip_expression)

    if bnip_expression:
        tokens = Lexer().create_tokens(bnip_expression)
        if transpiled_expression := transpile_bnip_expression(tokens):
            split_tokens = get_section_from_tokens(tokens)
            expression_obj = BNIPExpression(
                    raw=bnip_expression,
                    tokens=tokens,
                    transpiled=transpiled_expression,
                    should_id_transpiled=transpile_bnip_expression(split_tokens[BNipSections.PROP]),
                    should_pickup=transpile_bnip_expression(split_tokens[BNipSections.PROP], isPickUpPhase=True) # * Some stuff gets transpiled differently in the pickup phase
                )
            return expression_obj
    return None


def load_bnip_expression(bnip_expression: str):
    if (expression_obj := generate_expression_object(bnip_expression)) is not None:
        bnip_expressions.append(expression_obj)


    