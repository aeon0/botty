"""
    Provides actions to perform tests on items in game.
"""


import os
import re
import glob
import traceback
from logger import Logger
from dataclasses import dataclass
from nip.lexer import NipSections
from nip.tokens import TokenType
from nip.transpile import (
    prepare_nip_expression,
    transpile_nip_expression,
    get_section_from_tokens,
    NIPExpression,
    nip_expressions,
    load_nip_expression,
)

# ! The below imports are necessary, they are used within the eval statements. Your text editor probably is not showing them as not in use.
from nip.NTIPAliasQuality import NTIPAliasQuality
from nip.NTIPAliasClass import NTIPAliasClass
from nip.NTIPAliasClassID import NTIPAliasClassID
from nip.NTIPAliasFlag import NTIPAliasFlag
from nip.NTIPAliasStat import NTIPAliasStat
from nip.NTIPAliasType import NTIPAliasType
from nip.utils import find_unique_or_set_base



def should_keep(item_data) -> tuple[bool, str]:
    """Decides whether or not to keep an item.
    Args:
        item_data (dict): The item data.
    returns:
        tuple[bool, str]: A tuple containing the following:
            bool: Whether or not to keep the item.
            str: The raw expression to use for the keep condition.

    """
    for expression in nip_expressions:
        if eval(expression.transpiled):
            return True, expression.raw
    return False, ""

def _gold_pickup(item_data: dict, expression: NIPExpression) -> bool | None:
    res = None
    for i, token in enumerate(expression.tokens):
        if (
            token.type == TokenType.KeywordNTIPAliasStat
            and token.value == str(NTIPAliasStat["gold"])
            and "Amount" in item_data
            and item_data["Amount"] is not None
        ):
            try:
                read_gold = int(item_data["Amount"])
                operator = expression.tokens[i + 1].value
                desired_gold = int(expression.tokens[i + 2].value)
                res = eval(f"{read_gold} {operator} {desired_gold}")
            except Exception as e:
                Logger.warning(f"Error evaluating gold pickup condition: {e}")
            break
    return res


def _handle_pick_eth_sockets(item_data: dict, expression: NIPExpression) -> tuple[bool, str]:
    """Handles the pick condition for eth and sockets.
        Args:
            item_data (dict): The item data.
            expression (NIPExpression): The expression to use.
        Returns:
            tuple[bool, str]: A tuple containing the following:
                bool: Whether or not to keep the item.
                NipExpression: The expression object that was used to evaluate the condition.
        """
    expression_raw = prepare_nip_expression(expression.raw)
    all_tokens = expression.tokens

    tokens_by_section = get_section_from_tokens(all_tokens)
    eth_keyword_present = "ethereal" in expression_raw.lower()
    soc_keyword_present =  expression_raw.lower().count("[sockets]") == 1 # currently ignoring if there's socket logic; i.e., [sockets] == 0 || [sockets] == 5

    eth = 0 # * -1 = set to false, 0 = not set, 1 = set to true
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
            if token.type == TokenType.KeywordNTIPAliasStat and token.value == str(NTIPAliasStat["sockets"]):
                desired_sockets = int(tokens[i + 2].value)
                if (desired_sockets > 0 and not (desired_sockets == 1 and tokens[i + 1].value == "<")) or (desired_sockets == 0 and tokens[i + 1].value == ">"):
                    soc = 1
                else:
                    soc = -1
                break


    # pickup table:
    # * w = white, g = gray
    #         -1 eth  0 eth   1 eth
    # -1 soc    w      w,g      g
    #  0 soc   w,g     w,g      g
    #  1 soc    g       g       g

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


def should_pickup(item_data) -> tuple[bool, str]:
    """Decides whether or not to keep an item.
    Args:
        item_data (dict): The item data.
    returns:
        tuple[bool, str]: A tuple containing the following:
            bool: Whether or not to keep the item.
            str: The raw expression to use for the keep condition.
    """

    pick_eval_expr = ""
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

            property_condition = eval(pick_eval_expr) # * This string in the eval uses the item_data that is being passed in
            if property_condition:
                return True, expression.raw


    return False, ""


def should_id(item_data) -> bool:
    """Checks if the item should be identified.

        Args:
            item_data (dict): The item data.

        Returns: (bool):
            True if the item should be identified, False otherwise.

        Raises:
            None

        Examples:
            [name] == ring && [quality] == rare -> True
            [name] == ring && [quality] == rare # [strength] == 5 -> Falsep
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

def _load_nip_expressions(filepath):
    """
        Loads the NIP expressions from the file.
        Args:
            filepath (str): The path to the file.
        Returns:
            None
    """
    with open(filepath, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line == "" or line.startswith("//"): # Empty or comment line
                continue
            try:
                load_nip_expression(line)
            except Exception as e:
                filepath = filepath.replace("\\", "/")
                file = filepath.split('/config/')[1]
                print(f"{file}:{e}:line {i + 1}") # TODO look at these errors
                if False and traceback.print_exc(): # * Switch between True and False for debugging
                    break


default_nip_file_path = f"{os.getcwd()}/config/default.nip"
nip_path = f"{os.getcwd()}/config/nip"
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
        _load_nip_expressions(nip_file_path)
# fallback to default nip file if no custom nip files specified or existing files are excluded
else:
    num_files = 1
    _load_nip_expressions(default_nip_file_path)
    Logger.warning("No .nip files in config/nip/, fallback to default.nip")
Logger.info(f"Loaded {num_files} nip files with {len(nip_expressions)} total expressions.")

nip_expressions = sorted(nip_expressions, key=lambda x: len(x.raw))

if __name__ == "__main__":
    print(transpile_nip_expression("[name] == ring && [quality] == rare # [strength] == 5"))