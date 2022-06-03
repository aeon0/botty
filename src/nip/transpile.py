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
from logger import Logger

from nip.lexer import Lexer, NipSyntaxError, NipSections
from nip.tokens import TokenType

class NipSyntaxErrorSection(NipSyntaxError):
    def __init__(self, token, section):
        super().__init__(f"[ {token.type} ] : {token.value} can not be used in section [ {section} ].")


@dataclass
class NIPExpression:
    raw: str
    should_id_transpiled: str
    transpiled: str
    should_pickup: str

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


def transpile(tokens, isPickedUpPhase=False):
    expression = ""
    section_start = True
    for i, token in enumerate(tokens):
        if section_start:
            expression += "("
            section_start = False
        if token == None:
            continue
        if token.type == TokenType.NTIPAliasStat:
            if len(tokens) >= i + 2 and tokens[i + 2].type == TokenType.NUMBERPERCENT: # Look at the other side of the comparsion.
                # Write an expression to test make sure the item_data['Item']['NTIPAliasStatProps'] is a dict.
                stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
                stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"
                is_dict = eval(f"isinstance({stat_min_max}, dict)") # ghetto, but for now, ok..
                # if is_dict:
                    # expression += f"(int(({stat_value} - {stat_min_max}['min']) * 100.0 / ({stat_min_max}['max'] - {stat_min_max}['min'])))"
                # else:
                expression += f"(int(-1))" # Ignore it since it wasn't a dict and the user tried to use a %
            else:
                # stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
                # stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"
                # clamp value between min and max
                # expression += f"(({stat_value} >= {stat_min_max}['max'] and {stat_min_max}['max']) or ({stat_value} <= {stat_min_max}['min'] and {stat_min_max}['min']) or {stat_value})"
                # expression += f"(int(item_data['NTIPAliasStat']['{token.value}']))"
                expression += f"(int(item_data['NTIPAliasStat'].get('{token.value}', -1)))"
        elif token.type == TokenType.NTIPAliasClass:
            expression += f"(int(NTIPAliasClass['{token.value}']))"
        elif token.type == TokenType.NTIPAliasQuality:
            expression += f"(int(NTIPAliasQuality['{token.value}']))"
        elif token.type == TokenType.NTIPAliasClassID:
            expression += f"(int(NTIPAliasClassID['{token.value}']))"
        elif token.type == TokenType.NTIPAliasFlag:
            pass
            # we don't need the flag value here, it's used below
            # expression += f"NTIPAliasFlag['{token.value}']"
        elif token.type == TokenType.NTIPAliasType:
            expression += f"(int(NTIPAliasType['{token.value}']))"
        elif token.type == TokenType.IDNAME:
            if not isPickedUpPhase:
                expression += "(str(item_data['NTIPAliasIdName']).lower())"
        elif token.type == TokenType.NAME:
            expression += "(int(item_data['NTIPAliasClassID']))"
        elif token.type == TokenType.CLASS:
            expression += "(int(item_data['NTIPAliasClass']))"
        elif token.type == TokenType.QUALITY:
            expression += "(int(item_data['NTIPAliasQuality']))"
        elif token.type == TokenType.FLAG:
            if tokens[i + 2].type == TokenType.NTIPAliasFlag:
                condition_type = tokens[i + 1]
                if condition_type.type == TokenType.EQ:
                    expression += f"(item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
                elif condition_type.type == TokenType.NE:
                    expression += f"(not item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
            # Check if the flag we're looking for (i.e ethereal) is i + 2 away from here, if it is, grab it's value (0x400000) and place it inside the lookup.
        elif token.type == TokenType._TYPE:
            expression += "(int(item_data['NTIPAliasType']))"
        elif token.type == TokenType.EQ:
            if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                if not isPickedUpPhase:
                    expression += "=="
                else:
                    if not tokens[i - 1].type == TokenType.IDNAME:
                        expression += "=="
        elif token.type == TokenType.NE:
            if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                expression += "!="
        elif token.type == TokenType.GT:
            if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                expression += ">"
        elif token.type == TokenType.LT:
            if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                expression += "<"
        elif token.type == TokenType.GE:
            if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                expression += ">="
        elif token.type == TokenType.LE:
            if tokens[i + 1].type != TokenType.NTIPAliasFlag:
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
            if tokens[i - 2].type == TokenType.IDNAME:
                if isPickedUpPhase:
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
        tokens = Lexer().create_tokens(split_nip_expression[0])
        all_tokens.extend(tokens)
        for token in tokens:
            if token.type == TokenType.NTIPAliasStat:
                raise NipSyntaxErrorSection(token, "property")
    if split_nip_expression_len >= 2 and split_nip_expression[1]: # stats
        tokens = Lexer().create_tokens(split_nip_expression[1])
        all_tokens.extend(tokens)
        for token in tokens:
            is_invalid_stat_lookup = (
                token.type == TokenType.NTIPAliasClass or
                token.type == TokenType.NTIPAliasClassID and token.value != '523' or # 523 refers to gold
                token.type == TokenType.NTIPAliasFlag or
                token.type == TokenType.NTIPAliasType or
                token.type == TokenType.NTIPAliasQuality
            )

            if is_invalid_stat_lookup:
                raise NipSyntaxErrorSection(token, "stats")

    if split_nip_expression_len >= 3 and split_nip_expression[2]: # maxquantity
        tokens = Lexer().create_tokens(split_nip_expression[2])
        all_tokens.extend(tokens)
        for token in tokens:
            is_invalid_maxquantity_lookup = (
                token.type == TokenType.NTIPAliasClass or
                token.type == TokenType.NTIPAliasQuality or
                token.type == TokenType.NTIPAliasClassID or
                token.type == TokenType.NTIPAliasFlag or
                token.type == TokenType.NTIPAliasType or
                token.type == TokenType.NTIPAliasStat
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

def transpile_nip_expression(expression: str, isPickedUpPhase=False):
    expression = prepare_nip_expression(expression)
    if expression:
        tokens = list(Lexer().create_tokens(expression))
        transpiled_expression = transpile(tokens, isPickedUpPhase=isPickedUpPhase)
        if transpiled_expression:
            return transpiled_expression




nip_expressions: list[NIPExpression] = []

def load_nip_expression(nip_expression):
    transpiled_expression = transpile_nip_expression(nip_expression)
    if transpiled_expression:
        nip_expressions.append(
            NIPExpression(
                raw=nip_expression,
                should_id_transpiled=transpile_nip_expression(nip_expression.split("#")[0]),
                transpiled=transpiled_expression,
                should_pickup=transpile_nip_expression(nip_expression.split("#")[0], isPickedUpPhase=True)
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


def gold_pickup(item_data):
    for expression in nip_expressions:
        if expression.raw:
            if "[gold]" in expression.raw.lower():
                res = eval(expression.transpiled)
                if res:
                    return True, expression.raw
    return False, ""


def should_pickup(item_data):

    # * Handle the gold pickup.
    raw_expression = ""
    if item_data["BaseItem"]["DisplayName"] == "Gold":
        return gold_pickup(item_data)

    wants_open_socket = False # * If the nip expression is looking for a socket
    for expression in nip_expressions:
        if expression.raw:
            expression_raw = prepare_nip_expression(expression.raw)
            nip_expression_split = expression_raw.replace("\n", "").split("#")
            property_condition = None
            try:
                property_condition = eval(expression.should_pickup) # * This string in the eval uses the item_data that is being passed in
            except:
                pass
            if property_condition:
                return True, expression.raw

            if item_data["Color"] == "gray":
                if len(nip_expression_split) >= 2:
                    stats_expression = nip_expression_split[1]
                    if stats_expression:
                        # Loop through the tokens, and see if the [sockets] is > 0.
                        # You must check ==, >, <, >=, <=, != to see if we should pickup the socketed item.
                        tokens = list(Lexer().create_tokens(stats_expression))
                        for i, token in enumerate(tokens):
                            if token.type == TokenType.NTIPAliasStat and token.value == str(NTIPAliasStat["sockets"]):
                                if tokens[i + 1].value == ">" and tokens[i + 2].value >= 0 and tokens[i + 2].value <= 6:
                                    wants_open_socket = True
                                    raw_expression = expression.raw
                                    break
                                elif tokens[i + 1].value == "==" and tokens[i + 2].value > 0 and tokens[i + 2].value <= 6:
                                    wants_open_socket = True
                                    raw_expression = expression.raw
                                    break
                                elif tokens[i + 1].value == "<" and tokens[i + 2].value > 1 and tokens[i + 2].value <= 6:
                                    wants_open_socket = True
                                    raw_expression = expression.raw
                                    break
                                elif tokens[i + 1].value == "<=" and tokens[i + 2].value >= 1 and tokens[i + 2].value <= 6:
                                    wants_open_socket = True
                                    raw_expression = expression.raw
                                    break
                                elif tokens[i + 1].value == ">=" and tokens[i + 2].value >= 1 and tokens[i + 2].value <= 6:
                                    wants_open_socket = True
                                    raw_expression = expression.raw
                                    break
                                else:
                                    wants_open_socket = False
                                    raw_expression = ""
                                    break

    return wants_open_socket, raw_expression

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
    item_data = {
        "Name": "IMP STINGER",
        "Quality": "rare",
        "Text": "IMP STINGER|BLADE BOW|TWO-HAND DAMAGE: 36 TO 76|REQUIRED DEXTERITY: 119|REQUIRED STRENGTH: 76|REQUIRED LEVEL: 45|BOW CLASS - VERY FAST ATTACK SPEED|+10% INCREASED ATTACK SPEED|+75% ENHANCED DAMAGE|+5 TO MAXIMUM DAMAGE|+113 TO ATTACK RATING|+191% DAMAGE TO UNDEAD|+186 TO ATTACK RATING AGAINST UNDEAD|4% LIFE STOLEN PER HIT",
        "BaseItem": {
            "DisplayName": "Blade Bow",
            "NTIPAliasClassID": 265,
            "NTIPAliasType": 27,
            "NTIPAliasStatProps": {
                "194": {
                    "min": 0,
                    "max": 4
                },
                "72": 32,
                "73": 32,
                "23": 21,
                "24": 41
            },
            "dimensions": [
                2,
                3
            ],
            "NTIPAliasClass": 2
        },
        "Item": None,
        "NTIPAliasIdName": "IMPSTINGER",
        "NTIPAliasType": 27,
        "NTIPAliasClassID": 265,
        "NTIPAliasClass": None,
        "NTIPAliasQuality": 6,
        "NTIPAliasStat": {
            "21": 36,
            "22": 5,
            "122": 191,
            "19": 113,
            "124": 186,
            "18": 75,
            "93": 10,
            "60": 4
        },
        "NTIPAliasFlag": {
            "0x10": 1,
            "0x400000": 0,
            "0x4000000": 0
        }
    }
    # print(eval("(int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['bladebow']))or(int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['shadowbow']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['rare']))and(int(item_data['NTIPAliasStat'].get('93', 0)))>=(20.0)"))

    ex = '[name] == matriarchalbow || [name] == grandmatronbow || [name] == spiderbow || [name] == bladebow || [name] == shadowbow && [quality] == rare # [ias] >= 10'
    print(transpile_nip_expression(ex))
    print(
            _test_nip_expression(item_data, ex)

    )
    # print(((int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['bladebow']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['rare'])))and((int(item_data['NTIPAliasStat'].get('93', -1)))>=(11.0)))

    # print(((int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['bladebow']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['rare'])))and((int(item_data['NTIPAliasStat'].get('93', -1)))>=(1.0)))
    # * Should remove the maxquantity from the below expressions due to maxquantity not being used atm
    # print(transpile_nip_expression("[name] == ring && [quality] == rare # [strength] == 5"))
    # print(transpile_nip_expression("[name] == keyofterror"))
    # print(transpile_nip_expression("[name] == keyofterror # [strength] == 5 # [maxquantity] == 1"))


    # for i, test in enumerate(transpile_tests):
    #     try:
    #         assert transpile_nip_expression(test["raw"]) == test["transpiled"]
    #         print(f"transpile_test {i} passed.")
    #     except:
    #         print("Failed to transpile:", test["raw"])
    #         print(transpile_nip_expression(test["raw"]), end="\n\n")


    # print("\n")

    # for i, test in enumerate(syntax_error_tests):
    #     try:
    #         transpile_nip_expression(test["expression"])
    #         print(f"syntax_error_test {i} passed.")
    #     except:
    #         if not test["should_fail"]:
    #             print(f"{test['expression']} failed (unexpectedly failed)", end="\n\n")