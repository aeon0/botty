from nip.NTIPAliasQuality import NTIPAliasQuality
from nip.NTIPAliasClass import NTIPAliasClass
from nip.NTIPAliasClassID import NTIPAliasClassID
from nip.NTIPAliasFlag import NTIPAliasFlag
from nip.NTIPAliasStat import NTIPAliasStat
from nip.NTIPAliasType import NTIPAliasType

# ! The above imports are necessary, they are used within the eval statements. Your text editor probably is not showing them as not in use.
import os
import glob

from nip.lexer import Lexer
from nip.tokens import TokenType

def transpile(tokens):
    expression = ""
    for i, token in enumerate(tokens):
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
                expression += "and"
        elif token.type == TokenType.UNKNOWN:
            print(1111)
            print(tokens[i-2] ,token)
            if tokens[i - 2].type == TokenType.IDNAME:
                expression += f"(str('{token.value}').lower())"
            else:
                expression += "(-1)"
        else:
            expression += f"{token.value}"
        expression += "" # add space if spaces are needed
    return expression


class NipValidationError(Exception):
    def __init__(self, section, token_errored_on):
        self.section_errored_on = section
        self.token_errored_on = token_errored_on
    
    def __str__(self):
        return f"[ {self.token_errored_on.type} : {self.token_errored_on.value} ] can not be used in section [ {self.section_errored_on} ]."

def validate_nip_expression(nip_expression):
    """
        enforces that {property} # {stats} # {maxquantity}
    """
    tokens = None

    if not nip_expression:
        return 

    split_nip_expression = nip_expression.split("#")
    split_nip_expression_len = len(split_nip_expression)

    if split_nip_expression_len >= 1 and split_nip_expression[0]: # property
        tokens = Lexer().create_tokens(split_nip_expression[0])
        for token in tokens:
            if token.type == TokenType.NTIPAliasStat:
                raise NipValidationError("property", token)
    if split_nip_expression_len >= 2 and split_nip_expression[1]: # stats
        tokens = Lexer().create_tokens(split_nip_expression[1])
        for token in tokens:
            is_invalid_stat_lookup = (
                token.type == TokenType.NTIPAliasClass or
                token.type == TokenType.NTIPAliasClassID and token.value != '523' or # 523 refers to gold
                token.type == TokenType.NTIPAliasFlag or 
                token.type == TokenType.NTIPAliasType or 
                token.type == TokenType.NTIPAliasQuality
            )

            if is_invalid_stat_lookup:
                #print("-" * 30)
                raise NipValidationError("stats", token)

    if split_nip_expression_len >= 3 and split_nip_expression[2]: # maxquantity
        tokens = Lexer().create_tokens(split_nip_expression[2])

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
                raise NipValidationError("maxquantity", token)
    return True

def prepare_nip_expression(expression):
    if not expression.startswith("//") and not expression.startswith("-"):
        expression = expression.lower()
        expression = expression.split("//")[0] # * Ignore the comments inside the nip expression
        if validate_nip_expression(expression):
            return expression

def transpile_nip_expression(expression: str):
    expression = prepare_nip_expression(expression)
    if expression:
        tokens = list(Lexer().create_tokens(expression))
        transpiled_expression = transpile(tokens)
        if transpiled_expression:
            return transpiled_expression


nip_expressions = []
def load_nip_expression(nip_expression):
    transpiled_expression = transpile_nip_expression(nip_expression)
    if transpiled_expression:
        already_loaded = False
        for expression in nip_expressions:
            if expression["raw"] == nip_expression:
                already_loaded = True
        if not already_loaded:
            nip_expressions.append({
                "raw": nip_expression,
                "transpiled": transpiled_expression,
                "should_id_transpiled": transpile_nip_expression(nip_expression.split("#")[0])
            })


def should_keep(item_data):
    # print(item_data["NTIPAliasIdName"])
    for expression in nip_expressions:
        if expression["transpiled"]:
            print(expression["transpiled"])
            try:
                if eval(expression["transpiled"]):
                    # print(expression["raw"])
                    return True
            except:
                pass
                #print(f"Error: {expression['raw']}") # TODO look at this errors .. CHECKED NOT ERRORING FOR NOW..
    return False


def gold_pickup(item_data):
    for expression in nip_expressions:
        if expression["raw"]:
            if "[gold]" in expression["raw"].lower():
                res = eval(expression["transpiled"])
                if res:
                    return True
    return False


def should_pickup(item_data):
    # * Handle the gold pickup.
    if item_data["BaseItem"]["DisplayName"] == "Gold":
        return gold_pickup(item_data)


    wants_open_socket = False # * If the nip expression is looking for a socket
    for expression in nip_expressions:
        if expression["raw"]:
            expression = prepare_nip_expression(expression["raw"])
            nip_expression_split = expression.replace("\n", "").split("#")
            property_condition = None
            try:
                property_condition = eval(transpile_nip_expression(nip_expression_split[0])) # * This string in the eval uses the item_data that is being passed in
            except:
                pass
                #print(f"Error: {expression}")
            if property_condition:
                return True

            if item_data["Quality"] == "gray":
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
                                    break
                                elif tokens[i + 1].value == "==" and tokens[i + 2].value > 0 and tokens[i + 2].value <= 6:
                                    wants_open_socket = True
                                    break
                                elif tokens[i + 1].value == "<" and tokens[i + 2].value > 1 and tokens[i + 2].value <= 6:
                                    wants_open_socket = True
                                    break
                                elif tokens[i + 1].value == "<=" and tokens[i + 2].value >= 1 and tokens[i + 2].value <= 6:
                                    wants_open_socket = True
                                    break
                                elif tokens[i + 1].value == ">=" and tokens[i + 2].value >= 1 and tokens[i + 2].value <= 6:
                                    wants_open_socket = True
                                    break
                                else:
                                    # #print(1)
                                    wants_open_socket = False
                                    break
    
    return wants_open_socket
    
def should_id(item_data):
    """
        [name] == ring && [quality] == rare                     Don't ID.
        [name] == ring && [quality] == rare # [strength] == 5   Do ID.
    """
    id = False
    for expression in nip_expressions:
        try:
            if eval(expression["should_id_transpiled"]):
                # #print(expression["raw"])
                if len(expression["raw"].split("#")) > 1:
                    id = True
                    break
        except Exception as e:
            pass
            # #print(f"Error: {expression['raw']} {e}\n\n") # TODO look at these errors
    return id

def load_nip_expressions(filepath):
    with open(filepath, "r") as f:
        for line in f:
            try:
                load_nip_expression(line.strip())
            except Exception as e:
                pass
                # #print(e, "Errored on line:", line) # TODO look at these errors



nip_path = os.path.join(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), os.pardir)), 'nip')
glob_nip_path = os.path.join(nip_path, '**', '*.nip')
nip_file_paths = glob.glob(glob_nip_path, recursive=True)

# * Removes folders and files that begin with -
for filepath in nip_file_paths:
    split_filepath = filepath.split("\\")
    for i,dir in enumerate(split_filepath):
        if dir.startswith("-"):
            remove = "\\".join(split_filepath[:i + 1])
            nip_file_paths = [filepath for filepath in nip_file_paths if not filepath.startswith(remove)]

for nip_file_path in nip_file_paths:
    print(nip_file_path)
    load_nip_expressions(nip_file_path)


print(transpile_nip_expression("[idname]"))
print(f"Loaded {len(nip_expressions)} nip expressions.")

