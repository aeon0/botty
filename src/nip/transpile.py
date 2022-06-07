from ctypes import string_at
from dataclasses import dataclass
from distutils.log import error
from xmlrpc.client import Boolean
from nip.NTIPAliasQuality import NTIPAliasQuality
from nip.NTIPAliasClass import NTIPAliasClass
from nip.NTIPAliasClassID import NTIPAliasClassID
from nip.NTIPAliasFlag import NTIPAliasFlag
from nip.NTIPAliasStat import NTIPAliasStat
from nip.NTIPAliasType import NTIPAliasType
from nip.UniqueAndSetData import UniqueAndSetData
# ! The above imports are necessary, they are used within the eval statements. Your text editor probably is not showing them as not in use.
import os
import glob
import re
from itertools import groupby
from logger import Logger

from nip.lexer import Lexer, NipSyntaxError, NipSections
from nip.tokens import Token, TokenType

class NipSyntaxErrorSection(NipSyntaxError):
    def __init__(self, token, section):
        super().__init__(f"[ {token.type} ] : {token.value} can not be used in section [ {section} ].")

@dataclass
class NIPExpression:
    raw: str
    should_id_transpiled: str | None
    transpiled: str
    should_pickup: str | None
    tokens: list[Token]

def find_unique_or_set_base(unique_or_set_name) -> tuple[str, str]:
    unique_or_set_name = unique_or_set_name.lower()
    for key in UniqueAndSetData:
        if UniqueAndSetData[key].get("uniques"):
            for uniques in UniqueAndSetData[key]["uniques"]:
                for unique in uniques:
                    if unique.lower() == unique_or_set_name:
                        return key, "unique"
        if UniqueAndSetData[key].get("sets"):
            for sets in UniqueAndSetData[key]["sets"]:
                for set in sets:
                    if set.lower() == unique_or_set_name:
                        return key, "set"
    return "", ""


class NIPKeywords:
    NTIPAliasQuality = "NTIPAliasQuality"
    NTIPAliasClass = "NTIPAliasClass"
    NTIPAliasClassID = "NTIPAliasClassID"
    NTIPAliasFlag = "NTIPAliasFlag"
    NTIPAliasType = "NTIPAliasType"
    NTIPAliasStat = "NTIPAliasStat"
    NTIPAliasType = "NTIPAliasType"



def _create_nip_keyword_string(NTIPAlias) -> str:
    """keyword like [strength] or [sockets] ect"""
    return  f"(int(item_data['{NTIPAlias}']))"

def _create_nip_value_string(NTIPAlias, NTIPAliasKey) -> str:
    """value like ring or sorceressitem ect"""
    return f"(int({NTIPAlias}['{NTIPAliasKey}']))"


def transpile(tokens, isPickUpPhase=False):
    expression = ""
    section_start = True
    for i, token in enumerate(tokens):
        if section_start:
            expression += "("
            section_start = False
        if token == None:
            continue
        if token.type == TokenType.ValueNTIPAliasStat:
            if len(tokens) >= i + 2 and tokens[i + 2].type == TokenType.NUMBERPERCENT: # Look at the other side of the comparsion.
                expression += f"(int(-1))" # Ignore it since it wasn't a dict and the user tried to use a %
                # Write an expression to test make sure the item_data['Item']['NTIPAliasStatProps'] is a dict.
                # stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
                # stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"
                # is_dict = eval(f"isinstance({stat_min_max}, dict)") # ghetto, but for now, ok..
                # if is_dict:
                    # expression += f"(int(({stat_value} - {stat_min_max}['min']) * 100.0 / ({stat_min_max}['max'] - {stat_min_max}['min'])))"
                # else:
            else:
                expression += f"(int(item_data['NTIPAliasStat'].get('{token.value}', -1)))"
                # expression += _create_nip_value_string(token.value)
                # stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
                # stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"
                # clamp value between min and max
                # expression += f"(({stat_value} >= {stat_min_max}['max'] and {stat_min_max}['max']) or ({stat_value} <= {stat_min_max}['min'] and {stat_min_max}['min']) or {stat_value})"
                # expression += f"(int(item_data['NTIPAliasStat']['{token.value}']))"

        elif token.type == TokenType.ValueNTIPAliasFlag:
            pass
            # we don't need the flag value here, it's used below
            # expression += f"NTIPAliasFlag['{token.value}']"
        elif (token.type == TokenType.ValueNTIPAliasType or
             token.type == TokenType.ValueNTIPAliasClass or
             token.type == TokenType.ValueNTIPAliasQuality or
             token.type == TokenType.ValueNTIPAliasClassID):
            token_data = token.data()
            expression += _create_nip_value_string(token_data["type"].replace("Value", ""), token_data["value"])
            # expression += f"(int(NTIPAliasType['{token.value}']))"
        elif token.type == TokenType.KeywordNTIPAliasIDName:
            if not isPickUpPhase:
                expression += "(str(item_data['NTIPAliasIdName']).lower())"
        elif token.type == TokenType.KeywordNTIPAliasName:
            expression += "(int(item_data['NTIPAliasClassID']))"
        elif token.type == TokenType.KeywordNTIPAliasClass:
            expression += "(int(item_data['NTIPAliasClass']))"
            # token_data = token.data()
            # expression += _create_nip_keyword_string(token_data["type"].replace("Value", ""))
        elif token.type == TokenType.KeywordNTIPAliasQuality:
            expression += "(int(item_data['NTIPAliasQuality']))"
        elif token.type == TokenType.KeywordNTIPAliasFlag:
            if tokens[i + 2].type == TokenType.ValueNTIPAliasFlag:
                condition_type = tokens[i + 1]
                if condition_type.type == TokenType.EQ:
                    expression += f"(item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
                elif condition_type.type == TokenType.NE:
                    expression += f"(not item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
            # Check if the flag we're looking for (i.e ethereal) is i + 2 away from here, if it is, grab it's value (0x400000) and place it inside the lookup.
        elif token.type == TokenType.KeywordNTIPAliasType:
            # expression += "(int(item_data['NTIPAliasType']))"
            # NTIPAliasType["ring"] in item["NTIPAliasType"] and NTIPAliasType["ring"] or -1
            operator = tokens[i + 1]
            next_type = tokens[i + 2] # The type we're looking for
            expression += f"(int(NTIPAliasType['{next_type.value}']) in item_data['NTIPAliasType'] and int(NTIPAliasType['{next_type.value}']) or -1)"
        elif token.type == TokenType.EQ:
            if tokens[i + 1].type != TokenType.ValueNTIPAliasFlag:
                if not isPickUpPhase:
                    expression += "=="
                else:
                    if not tokens[i - 1].type == TokenType.KeywordNTIPAliasIDName:
                        expression += "=="
        elif token.type == TokenType.NE:
            if tokens[i + 1].type != TokenType.ValueNTIPAliasFlag:
                expression += "!="
        elif token.type == TokenType.GT:
            if tokens[i + 1].type != TokenType.ValueNTIPAliasFlag:
                expression += ">"
        elif token.type == TokenType.LT:
            if tokens[i + 1].type != TokenType.ValueNTIPAliasFlag:
                expression += "<"
        elif token.type == TokenType.GE:
            if tokens[i + 1].type != TokenType.ValueNTIPAliasFlag:
                expression += ">="
        elif token.type == TokenType.LE:
            if tokens[i + 1].type != TokenType.ValueNTIPAliasFlag:
                expression += "<="
        elif token.type == TokenType.NUMBER:
            expression += f"({token.value})"
        elif token.type == TokenType.NUMBERPERCENT:
            expression += f"int({token.value})"
        elif token.type == TokenType.AND:
            if tokens[i - 1].type != TokenType.AND:
                expression += "and"
        elif token.type == TokenType.SECTIONAND:
            if tokens[i - 1].type != TokenType.SECTIONAND:
                expression += ")"
                expression += "and"
                section_start = True
        elif token.type == TokenType.UNKNOWN:
            if tokens[i - 2].type == TokenType.KeywordNTIPAliasIDName:
                if isPickUpPhase:
                    base, quality = find_unique_or_set_base(token.value)
                    expression += f"(int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['{base}']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['{quality}']))"
                else:
                    expression += f"(str('{token.value}').lower())"
            else:
                expression += "(-1)"
        else:
            expression += f"{token.value}"
        expression += "" # add space if spaces are needed
    expression += ")" # * Close the last bracket since there is no other section and to close it.
    return expression


    

class NipValidationError(Exception):
    def __init__(self, section, token_errored_on):
        self.section_errored_on = section
        self.token_errored_on = token_errored_on

    def __str__(self):
        return f"[ {self.token_errored_on.type} : {self.token_errored_on.value} ] can not be used in section [ {self.section_errored_on} ]."


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
    for i, token in enumerate(all_tokens):
        if token.type == TokenType.EQ:
            if i == len(all_tokens) - 1: # * Check to make sure the next token is a token.
                raise NipSyntaxError("No value after equal sign")

    return True


def remove_quantity(expression): # ! This is a bit ghetto, but since we're not using the maxquantity, we can just remove it.
    split_expression = expression.split("#")
    if len(split_expression) == 3:
        split_expression = (split_expression[0] + "#" + split_expression[1]).split("#")
        if len(split_expression[1]) <= 1:
            return split_expression[0]
        else:
            return "#".join(split_expression)
    return expression

def prepare_nip_expression(expression: str) -> str:
    if not expression.startswith("//") and not expression.startswith("-"):
        expression = expression.lower()
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




nip_expressions: list[NIPExpression] = []

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



def load_nip_expression(nip_expression):
    nip_expression = prepare_nip_expression(nip_expression)
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
                should_pickup=transpile_nip_expression(split_tokens[NipSections.PROP], isPickUpPhase=True)
            )
        )

def should_keep(item_data):
    for expression in nip_expressions:
        try:
            if eval(expression.transpiled):
                return True, expression.raw
        except:
            pass
            #print(f"Error: {expression.raw}") # TODO look at this errors .. CHECKED NOT ERRORING FOR NOW..
    return False, ""


def _gold_pickup(item_data: dict, expression: NIPExpression) -> bool | None:
    res = None
    for i, token in enumerate(expression.tokens):
        if token.type == TokenType.ValueNTIPAliasStat and token.value == str(NTIPAliasStat["gold"]):
            read_gold = int(item_data["Amount"])
            operator = expression.tokens[i + 1].value
            desired_gold = int(expression.tokens[i + 2].value)
            res = eval(f"{read_gold} {operator} {desired_gold}")
            break
    return res


def _handle_pick_eth_sockets(item_data: dict, expression: NIPExpression) -> tuple[bool, str]:
    expression_raw = prepare_nip_expression(expression.raw)
    all_tokens = expression.tokens

    # Check to see if there is any None types in the tokens.
    # if None in all_tokens:
    #     print(all_tokens)
    #     Logger.error("None type found in tokens " + expression_raw)

    tokens_by_section = get_section_from_tokens(all_tokens)
    eth_keyword_present = "ethereal" in expression_raw.lower()
    soc_keyword_present =  expression_raw.lower().count("[sockets]") == 1 # currently ignoring if there's socket logic; i.e., [sockets] == 0 || [sockets] == 5

    eth = 0 # -1 = set to false, 0 = not set, 1 = set to true
    soc = 0
    if eth_keyword_present:
        for i, token in enumerate(tokens := tokens_by_section[NipSections.PROP]):
            if token.type == TokenType.ValueNTIPAliasFlag and str(token.value).lower() == "ethereal":
                if tokens[i - 1].value == "==":
                    eth = 1
                else:
                    eth = -1
                break

    if len(tokens_by_section) > 1 and soc_keyword_present:
        for i, token in enumerate(tokens := tokens_by_section[NipSections.STAT]):
            # print(f"tokens: {tokens}")
            if token.type == TokenType.ValueNTIPAliasStat and token.value == str(NTIPAliasStat["sockets"]):
                desired_sockets = int(tokens[i + 2].value)
                if (desired_sockets > 0 and not (desired_sockets == 1 and tokens[i + 1].value == "<")) or (desired_sockets == 0 and tokens[i + 1].value == ">"):
                    soc = 1
                else:
                    soc = -1
                break
    """
        pickup table:
                -1 eth  0 eth   1 eth
        -1 soc    w      w,g      g
         0 soc   w,g     w,g      g
         1 soc    g       g       g
    """

    ignore = 0
    if item_data["Color"] == "white":
        ignore = eth == 1 or soc == 1
    elif item_data["Color"] == "gray":
        ignore = eth == soc == -1

    pick_eval_expr = expression.should_pickup
    # print(f"color: {item_data['Color']}, eth: {eth}, soc: {soc}, ignore: {ignore}")
    if not ignore and eth_keyword_present:
        # remove ethereal from expression
        raw = expression.raw.replace("&& [flag]", "[flag]").replace("|| [flag]", "[flag]")
        raw = re.sub(r"\[flag\] (==|!=)\sethereal", "", raw)
        # print(f"Modified raw expression: {raw}")
        pick_eval_expr = transpile_nip_expression(raw.split("#")[0], isPickUpPhase=True)
        # print(f"Modified transpiled expression: {pick_eval_expr}")

    return ignore, pick_eval_expr


def should_pickup(item_data):
    item_is_gold = item_data["BaseItem"]["DisplayName"] == "Gold"
    for expression in nip_expressions:
        if expression.raw:
            # check gold
            if item_is_gold and "[gold]" in expression.raw.lower():
                if (res := _gold_pickup(item_data, expression)) is not None:
                    return res, expression.raw
            # check eth / sockets
            pick_eval_expr = expression.should_pickup
            if any(substring == item_data["Color"] for substring in ["white", "gray"]):
                ignore, pick_eval_expr = _handle_pick_eth_sockets(item_data, expression)
                if ignore:
                    continue
            try:
                property_condition = eval(pick_eval_expr) # * This string in the eval uses the item_data that is being passed in
                if property_condition:
                    return True, expression.raw
            except:
                pass

    return False, ""




def should_id(item_data):
    """
        [name] == ring && [quality] == rare                     Don't ID.
        [name] == ring && [quality] == rare # [strength] == 5   Do ID.
    """
    id = True

    for expression in nip_expressions:
        split_expression = expression.raw.split("#")
        try:
            if "[idname]" in expression.raw.lower():
                    id = True
                    return id
            if eval(expression.should_id_transpiled):
                if len(split_expression) == 1:
                    id = False
                    return id
        except Exception as e:
                print(f"Error: {expression.raw} {e}\n\n") # TODO look at these errors
        return id

def load_nip_expressions(filepath):
    with open(filepath, "r") as f:
        for i, line in enumerate(f):
            try:
                load_nip_expression(line.strip())
            except Exception as e:
                file = filepath.split('\\config/')[1].replace("/", "\\")
                print(f"{file}:{e}:line {i + 1}") # TODO look at these errors


def _test_nip_expression(item_data, raw_nip_expression):
    try:
        if eval(transpile_nip_expression(raw_nip_expression)):
            return True
    except:
        pass
    return False


default_nip_file_path = os.path.join(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), os.pardir)), 'config/default.nip')
nip_path = os.path.join(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), os.pardir)), 'config/nip')
glob_nip_path = os.path.join(nip_path, '**', '*.nip')
nip_file_paths = glob.glob(glob_nip_path, recursive=True)

# * Remove all directories or files that are in the .nipignore file from nip_file_paths. (accepts glob patterns)
if os.path.isfile(os.path.join(nip_path, '.nipignore')):
    with open(os.path.join(nip_path, '.nipignore'), "r") as f:
        for line in f:
            line = line.strip()
            line = line.replace("/", "\\")
            remove_files = glob.glob(os.path.join(nip_path, line), recursive=True)
            for remove_file in remove_files:
                if remove_file in nip_file_paths:
                    nip_file_paths.remove(remove_file)

num_files = 0
# load all nip expressions
if len(nip_file_paths) > 0:
    num_files = len(nip_file_paths)
    for nip_file_path in nip_file_paths:
        load_nip_expressions(nip_file_path)
# fallback to default nip file if no custom nip files specified or existing files are excluded
else:
    num_files = 1
    load_nip_expressions(default_nip_file_path)
    Logger.warning("No .nip files in config/nip/, fallback to default.nip")
Logger.info(f"Loaded {num_files} nip files with {len(nip_expressions)} total expressions.")


if __name__ == "__main__":
    item_data = {'Name': 'Stamina Potion', 'Color': 'white', 'Quality': 'normal', 'Text': 'STAMINA POTION', 'Amount': None, 'BaseItem': {'DisplayName': 'Stamina Potion', 'NTIPAliasClassID': 513, 'NTIPAliasType': 79, 'dimensions': [1, 1]}, 'Item': None, 'NTIPAliasType': [80, 9], 'NTIPAliasClassID': 513, 'NTIPAliasClass': None, 'NTIPAliasQuality': 2, 'NTIPAliasFlag': {'0x10': False, '0x4000000': False, '0x400000': False}}

    # print(transpile_nip_expression("[Name] == Grandcharm && [Quality] == Magic # [Itemaddskilltab] >= 1"))