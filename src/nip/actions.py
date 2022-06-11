from nip.NTIPAliasQuality import NTIPAliasQuality
from nip.NTIPAliasClass import NTIPAliasClass
from nip.NTIPAliasClassID import NTIPAliasClassID
from nip.NTIPAliasFlag import NTIPAliasFlag
from nip.NTIPAliasStat import NTIPAliasStat
from nip.NTIPAliasType import NTIPAliasType

# ! The above imports are necessary, they are used within the eval statements. Your text editor probably is not showing them as not in use.
import os
import glob
import re
import traceback
from itertools import groupby
from dataclasses import dataclass

from nip.lexer import Lexer, NipSyntaxError, NipSections
from nip.tokens import Token, TokenType
from nip.transpile import (
    prepare_nip_expression,
    transpile_nip_expression,
    get_section_from_tokens,
    NIPExpression,
    nip_expressions,
    load_nip_expression,

    OPENING_PARENTHESIS_COUNT
)
from nip.utils import find_unique_or_set_base
from logger import Logger

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


def should_keep(item_data):
    for expression in nip_expressions:
        if eval(expression.transpiled):
            return True, expression.raw
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
            except Exception as e:
                print(e,expression,)
                return
            if property_condition:
                return True, expression.raw
       

    return False, ""


def should_id(item_data):
    """
        [name] == ring && [quality] == rare                     Don't ID.
        [name] == ring && [quality] == rare # [strength] == 5   Do ID.
    """
    for expression in nip_expressions:
        if expression and expression.should_id_transpiled:
            split_expression = expression.raw.split("#")
            if "[idname]" in expression.raw.lower():
                    return True
            if len(split_expression) == 1:
                if eval(expression.should_id_transpiled):
                    return False
    return True


def load_nip_expressions(filepath):
    with open(filepath, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line == "" or line.startswith("//"): # Empty or comment line
                continue
            try:
                load_nip_expression(line)
            except Exception as e:
                file = filepath.split('\\config/')[1].replace("/", "\\")
                print(f"{file}:{e}:line {i + 1}") # TODO look at these errors
                if False and traceback.print_exc(): # * Switch between True and False for debugging
                    break
                




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
    # ((int(NTIPAliasType['gloves']) in item_data['NTIPAliasType'] and int(NTIPAliasType['gloves']) or -1)==(int(NTIPAliasType['gloves']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['rare']))and(item_data['NTIPAliasFlag']['0x400000']))and((int(item_data['NTIPAliasStat'].get('16', -1)))>=(180.0)and(int(item_data['NTIPAliasStat'].get('252', -1)))>=and((int(item_data['NTIPAliasStat'].get('16', -1)))>=(200.0)or(int(item_data['NTIPAliasStat'].get('93', -1)))>=(10.0)or((int(item_data['NTIPAliasStat'].get('2', -1)))+(int(item_data['NTIPAliasStat'].get('0', -1)))>=(10.0))or(int(item_data['NTIPAliasStat'].get('74', -1)))>=(5.0)or(int(item_data['NTIPAliasStat'].get('188,1', -1)))==(2.0)or(int(item_data['NTIPAliasStat'].get('188,2', -1)))==(2.0)or((int(item_data['NTIPAliasStat'].get('43', -1)))+(int(item_data['NTIPAliasStat'].get('39', -1)))+(int(item_data['NTIPAliasStat'].get('41', -1)))>=(20.0))))
    # [Name] == Demonhead && [Quality] == Unique && [Flag] == Ethereal # [Strength] >= 30 && [Lifeleech] >= 10    		// Eth Andariel'S Visage
    # ([Name] == Demonhead || [Name] == Bonevisage || [Name] == Diadem) && [Quality] <= Superior # [Enhanceddefense] > 0 && [Sockets] == 3
    # ([Name] == Demonhead || [Name] == Bonevisage || [Name] == Spiredhelm || [Name] == Corona) && [Quality] == Magic # [Itemtohitpercentperlevel] >= 1 && ([Fhr] == 10 || [Maxhp] >= 30)      // Visionary Helmet Of X
    # [Name] == Demonhead && [Quality] == Unique && [Flag] != Ethereal # [Strength] >= 30 && [Lifeleech] >= 10    		// Andariel'S Visage
    
    # print(nip_expressions[0].should_id_transpiled)
    # print(nip_expressions[0].transpiled)
    print(
        transpile_nip_expression("[name] == LargeCharm# [itemmagicbonus] >= 6 && [frw] >= 5")
    )