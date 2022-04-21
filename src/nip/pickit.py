from NTIPAliasQuality import NTIPAliasQuality
from NTIPAliasClass import NTIPAliasClass
from NTIPAliasClassID import NTIPAliasClassID
from NTIPAliasFlag import NTIPAliasFlag
from NTIPAliasStat import NTIPAliasStat
from NTIPAliasType import NTIPAliasType

import re
import json
import string

d2data_item = json.loads("""{
    "name": "WAR TRAVELER",
    "quality": "unique",
    "d2data":
    {
        "BaseItem":
        {
            "display_name": "Battle Boots",
            "item_class": "exceptional",
            "props": [
                {
                    "max": 18,
                    "min": 18,
                    "par": null,
                    "prop": "durability"
                },
                {
                    "max": 47,
                    "min": 39,
                    "par": null,
                    "prop": "defense"
                },
                {
                    "max": 1,
                    "min": 0,
                    "par": null,
                    "prop": "ethereal"
                }
            ],
            "sets": ["aldurs_advance"],
            "type": "boots",
            "uniques": ["war_traveler"]
        },
        "Item":
        {
            "base": "battle_boots",
            "display_name": "War Traveler",
            "props": [
                {
                    "max": 10,
                    "min": 10,
                    "par": 0,
                    "prop": "vit"
                },
                {
                    "max": 10,
                    "min": 10,
                    "par": 0,
                    "prop": "str"
                },
                {
                    "max": 50,
                    "min": 30,
                    "par": 0,
                    "prop": "mag%"
                },
                {
                    "max": 30,
                    "min": 30,
                    "par": 0,
                    "prop": "dur"
                },
                {
                    "max": 25,
                    "min": 25,
                    "par": 0,
                    "prop": "move2"
                },
                {
                    "max": 190,
                    "min": 150,
                    "par": 0,
                    "prop": "ac%"
                },
                {
                    "max": 25,
                    "min": 15,
                    "par": 0,
                    "prop": "dmg-norm"
                },
                {
                    "max": 10,
                    "min": 5,
                    "par": 0,
                    "prop": "thorns"
                },
                {
                    "max": 40,
                    "min": 40,
                    "par": 0,
                    "prop": "stamdrain"
                }
            ]
        },
        "ItemModifiers":
        {
            "defense": [139],
            "durability": [[13, 48]],
            "move1": [25],
            "dmg-norm": [[15, 25]],
            "ac%": [190],
            "str": [10],
            "vit": [10],
            "stamdrain": [40],
            "thorns": [10],
            "mag%": [50]
        }
    },
    "nip":
    {
        "NTIPAliasClassID": 388,
        "NTIPAliasClass": 1,
        "NTIPAliasQuality": 7,
        "NTIPAliasStat":
        {
            "21": 15,
            "22": 25,
            "78": 10,
            "31": 139,
            "72": 13,
            "73": 48,
            "80": 50,
            "0": 10,
            "3": 10,
            "16": 190,
            "96": 25,
            "154": 40
        },
        "NTIPAliasFlag":
        {
            "0x10": true,
            "0x4000000": false
        }
    }
}""")


def quote(s):
    return '"%s"' % s

def get_nipItem_prop(dict, index):
    try:
        return dict[str(index)]
    except (IndexError, KeyError):
        return "-1" # Return -1 here because the [key] in the expression does not exist, meaning that this should never be true.


def find_substring(needle, haystack):
    """
        fastest find substring fn i've found for whole words
        https://stackoverflow.com/a/4155029/12354066
    """
    index = haystack.find(needle)
    if index == -1:
        return False
    if index != 0 and haystack[index-1] not in string.whitespace:
        return False
    L = index + len(needle)
    if L < len(haystack) and haystack[L] not in string.whitespace:
        return False
    return index




# def replace_all_whole_words(needle, replacement, haystack):
#     # Escape special chars.
#     needle = re.escape(needle)
#     return re.sub(r"\b%s\b" % needle, replacement, haystack)

# def replace_all_whole_words(needle, replacement, haystack):
#     # Escape special chars.
#     needle = re.escape(needle)
#     return re.sub(r"\b%s\b" % needle, replacement, haystack)


def replace_all_whole_words(needle, replacement, haystack):
    split = haystack.split(" ")
    for i, word in enumerate(split):
        if word == needle:
            split[i] = replacement
    return " ".join(split)


"""
    TODO:
        add [flag]  support (NTIPAliasFlag) - done
        add [class] support (NTIPAliasClass) - not done
        add [type]  support(NTIPAliasType) - wait for 

        extensive testing
        adding attr % when Ezro adds the needed nip stuff.
        
        when everything is working:
        add variable functionality
        add function functionality

        look into security measures to take since we're using eval

        possibly add if functionality somehow.. (maybe like python does it with indents, or a ! in front of the line..) im not really thrilled on this idea
        
        add testing of the the client's pickit file using a dummy d2_data obj and see if the nip expresssions are valid, if not hopefully tell them which line fucked up..


"""
class StrArithmetic:
    """
        StrAdd("32") + StrAdd("32") = "64"
        StrAdd("96") - StrAdd("32") = "64"
        StrAdd("32") * StrAdd("2") = "64"
        StrAdd("128") / StrAdd("2") = "64"

        etc
    """
    def __init__(self, s):
        self.s = str(s)

    def __add__(self, y):
        y = isinstance(y, int) and StrArithmetic(y) or y
        return StrArithmetic(int(self.s) + int(y.s))

    def __mul__(self, y):
        y = isinstance(y, int) and StrArithmetic(y) or y
        return StrArithmetic(int(self.s) * int(y.s))

    def __sub__(self, y):
        y = isinstance(y, int) and StrArithmetic(y) or y
        return StrArithmetic(int(self.s) - int(y.s))

    def __floordiv__(self, y):
        y = isinstance(y, int) and StrArithmetic(y) or y
        return StrArithmetic(int(self.s) // int(y.s))
    
    def __truediv__(self, y):
        y = isinstance(y, int) and StrArithmetic(y) or y
        return StrArithmetic(float(self.s) / float(y.s))

    def __mod__(self, y):
        y = isinstance(y, int) and StrArithmetic(y) or y
        return StrArithmetic(int(self.s) % int(y.s))
    
    def __pow__(self, y):
        y = isinstance(y, int) and StrArithmetic(y) or y
        return StrArithmetic(int(self.s) ** int(y.s))

    def __lt__(self, y):
        return str(self.s) < str(y.s)

    def __le__(self, y):
        return str(self.s) <= str(y.s)
    
    def __eq__(self, y):
        return str(self.s) == str(y.s)
    
    def __ne__(self, y):
        return str(self.s) != str(y.s)
    
    def __ge__(self, y):
        return str(self.s) >= str(y.s)

    def __gt__(self, y):
        return str(self.s) > str(y.s)
    
    def __str__(self):
        return self.s
    
    def __int__(self):
        return int(self.s)

    def __float__(self):
        return float(self.s)

    def __bool__(self):
        return bool(self.s)

    
    
    
    
    

def add_multi_operator_syntax(expression):
    """
        input     ->  output
        "a | b"   -> "a or b"
        "a || b"  -> "a or b"
        "a or b"  -> "a or b"

        "a & b"   -> "a and b"
        "a && b"  -> "a and b"
        "a and b" -> "a and b"


        "a & b || c | d and e && f or g"  -> "a and b or c or d and e and f or g"

        there will most likely be some extra white space, but that's ok..
    """
    i=0
    while len(expression) > i + 2:
        prev_char = expression[i - 1] or ""
        curr_char = expression[i]
        next_char = expression[i+1] or ""
        if curr_char == "!":
            if next_char != "=":
                expression = expression[:i] + " not " + expression[i+1:]
                i+=5
        elif prev_char != "&" and  curr_char == "&":
            if next_char != "&":
                expression = expression[:i] + " and " + expression[i+1:]
                i+=5
        elif curr_char == "|":
            if prev_char != "|" and next_char != "|":
                expression = expression[:i] + " or " + expression[i+1:]
                i+=1
        elif curr_char == "=":
            if next_char != "=" and prev_char != ">" and next_char != ">" and prev_char != "!":
                expression = expression[:i-1] + " == " + expression[i+1:]
                i+=1
        elif curr_char == ">":
            if next_char == "=":
                expression = expression[:i] + " >= " + expression[i+2:]
                i+=2
            else:
                expression = expression[:i] + " > " + expression[i+1:]
                i+=2
        elif curr_char == "<":
            if next_char == "=":
                expression = expression[:i] + " <= " + expression[i+2:]
                i+=2
            else:
                expression = expression[:i] + " < " + expression[i+1:]
                i+=2
        i+=1
    
    expression = expression.replace("&&", " and ")
    expression = expression.replace("||", " or ")

    return expression



def handle_property_conditions(property_conditions):
    """
        handles the first part of the nip expression
        -> properties <- # stats # maxquantity
    """
    property_conditions = property_conditions.replace('[name]', " item['nip']['NTIPAliasClassID'] ")
    property_conditions = property_conditions.replace('[quality]', " item['nip']['NTIPAliasQuality'] ")
    # possibly look at using find_subtring instead of "in" when implementing variables and functions.
    
    for quality_name_alias in NTIPAliasQuality:
        if find_substring(quality_name_alias, property_conditions):
            property_conditions = property_conditions.replace(str(quality_name_alias), f" NTIPAliasQuality['{str(quality_name_alias)}'] ")
            break

    _property_conditions = property_conditions.replace("(", "").replace(")", "")
    for item_name_alias in NTIPAliasClassID:
        # replace the '(' and ')' in property_conditions just in case it looks like this ([name] == doubleaxe)
        if find_substring(item_name_alias, _property_conditions): # item_name_alias in conditions[i].split():
            property_conditions = replace_all_whole_words(item_name_alias, f" NTIPAliasClassID['{item_name_alias}'] ", property_conditions)
        

    
    return property_conditions

def handle_stat_conditions(stat_conditions):
    """
        handles the second part of the nip expression
        properties # -> stats <- # maxquantity

        finds stats i.e [vitality], [strength],[type] [class], and replaces them with the appropriate value
    """
    stats = re.compile(r"\[(.*?)\]").findall(stat_conditions)
    for stat in stats:
        try:
            if stat == "flag": # TODO LOOK AT THIS BC WE DO THIS IN ANOTHER FN TOO
                for key in NTIPAliasFlag:
                    if find_substring(key, stat_conditions):
                        stat_conditions = stat_conditions.replace("[flag]", f" get_nipItem_prop(item['nip']['NTIPAliasFlag'], '{str(NTIPAliasFlag[key])}') ") 
                        # replace the [flag] with the value from the d2data obj
                        stat_conditions = stat_conditions.replace(key, f" NTIPAliasFlag['{key}'] ")
                        # replace the flag name, i.e eth, etheral with the reference to value i.e 0x10, 0x4000000
            elif NTIPAliasStat[stat] or NTIPAliasStat[stat] == 0:
                if stat in stat_conditions:
                    stat_conditions = stat_conditions.replace(f"[{stat}]", f" get_nipItem_prop(item['nip']['NTIPAliasStat'], '{str(NTIPAliasStat[stat])}') ")
        except (KeyError, IndexError):
            stat_conditions = stat_conditions.replace(f"[{stat}]", "-1") # Return -1 here because the [key] in the expression does not exist, meaning that this should never be true.
        
    return stat_conditions






def handle_nip_expression(nip_expression):
    """
        handles the the stuff that should be done to all the segements of the nip expression
        -> properties # stats # maxquantity <-

        finds maxquantity i.e [maxquantity], and replaces it with the appropriate value
    """
        
    # create a regex that finds [flag]
    found_flags_tags = re.compile(r"\[flag\]").findall(nip_expression)
    if found_flags_tags:
        for flag_type in NTIPAliasFlag:
            if find_substring(flag_type, nip_expression):
                # replace the [flag] with the value from the d2data obj
                nip_expression = nip_expression.replace("[flag]", f" get_nipItem_prop(item['nip']['NTIPAliasFlag'], '{str(NTIPAliasFlag[flag_type])}') ") 
                # replace the flag name, i.e eth, etheral with the reference to value i.e 0x10, 0x4000000
                nip_expression = nip_expression.replace(flag_type, f" NTIPAliasFlag['{flag_type}'] ")
    
    nip_expression = nip_expression.replace("//", "#") # enable comment functionality
    nip_expression = add_multi_operator_syntax(nip_expression)


    
    # Get the words that are not words like "str(item['nip']['NTIPAliasQuality'])" or "NTIPAliasQuality['rare']"
    # Also don't get the keywords like ">" or "==" or "not" or "and" or "or", ect...
    # this way we will only find invalid words that were never found and replaced.
    keywords = [
        "(", ")", 
        ">", ">=", 
        "<", "<=", 
        "==", "=",
        "!=", "not",
        "&", "&&", "and",
        "|", "||", "or",
        "True", "False",
        "#", "//",
        "+", "-", "*", "/", "%"
    ]
    split = nip_expression.split(" ")
    
    for word in split:
        word = word.replace("(", "").replace(")", "")
        if len(word) > 0 and word[0] == "#":
            break
        # Make sure none of the keywords are in the word. Use find_substring since it should be faster.
        is_keyword = False
        for keyword in keywords:
            if keyword == word:
                is_keyword = True
                break

        surrounded_by_quotes = re.compile(r'^["\'](.*?)["\']$').match(word)
        
        # Create a regex to see if the char to the left of the digit is a +, -, *, .,
        is_digit = (word.isdigit() or re.findall(r'([\.\+\-\/\*]\d+)', word)) and True or False
        if is_digit:
            nip_expression = replace_all_whole_words(word, f"{word}", nip_expression)
        # find words that are followed by a '(' char or a '[' char.
        regex = re.compile(r"([a-zA-Z0-9_]+)([\(|\[])")
        is_undefined_word = word != "" and not is_digit and not regex.match(word) and not surrounded_by_quotes and not is_keyword
        if is_undefined_word:
            # print(f"\t{word} not defined", is_digit)
            # print(f"{word} was not found in the nip expression.")
             # Return -1 here because the [key] in the expression does not exist, meaning that this should never be true.
             # Replace the word if it matches the whole word OR at the end of the word a ')' char is found.
            nip_expression = replace_all_whole_words(word, f" -1 ", nip_expression)
            nip_expression = replace_all_whole_words(word+")", f" -1)", nip_expression)
            nip_expression = replace_all_whole_words(word+"]", f" -1]", nip_expression)

        
    return nip_expression

def handle_quantity_conditions(quantity_conditions):
    """
        handles maxquantity part of the nip expression
        properties # stats # -> maxquantity <-
    """
    pass

def build_expression(expression):
    conditions = expression.lower().split("#")
    expression = expression.replace("'", "\\'").replace("\"", "\\\"") # escape strings (since we're in eval)
    
    regex = re.compile(r"\[(.*?)\]") # gets the text between brackets, ["text"] -> text
    pythonic_property_conditions, pythonic_stat_conditions, pythonic_maxqaunity_conditions = "","",""
    
    for i in range(3):
        try:
            if conditions[i]:
                if i == 0:
                    pythonic_property_conditions = handle_property_conditions(conditions[0])
                elif i == 1:
                    pythonic_stat_conditions = handle_stat_conditions(conditions[1])
                elif i == 2:
                    pass
        except IndexError:
            pass

    # adds 'and' between the conditions if the condition is not empty
    pythonic_expression = f""" 
        {pythonic_property_conditions}
        {len(pythonic_stat_conditions) > 0 and ('and' + pythonic_stat_conditions) or ''}
        {len(pythonic_maxqaunity_conditions) > 0 and ('and' + pythonic_maxqaunity_conditions) or ''}
    """.replace("\n", "") # remove the newlines I just created.. readability..
    # print(pythonic_expression)

    pythonic_expression = handle_nip_expression(pythonic_expression)

    return pythonic_expression


def preprocess_nip_expression(nip_expressions) -> list:
    """
        Takes a list of nip expressions and creates a list of pythonic expressions
    """
    def should_skip_expression(expression):
        # skip expressions that start with an '_'
        return (expression.startswith("//") or expression == "\n" or 
        expression == "" or 
        len(expression) < 2 or 
        expression.find("[class]") >= 0 or 
        expression.find('[type]') >= 0 or 
        expression.find('[maxquantity]') >= 0 or 
        expression.find("color") >= 0)

    valid_expressions = []
    
    for nip_expression in nip_expressions:
        if not should_skip_expression(nip_expression):
            nip_expression = nip_expression.strip("\n\r")
            valid_expressions.append({
                "pythonic_expression": build_expression(nip_expression),
                "nip_expression": nip_expression
            })
    return valid_expressions

def preprocess_nip_file(nip_file_path):
    """
        Takes a .nip file ext and returns a list of pythonic expressions
    """
    with open(nip_file_path, "r") as f:
        return preprocess_nip_expression(f.readlines())

# item = d2data_item

item = json.loads("""{
    "name": "RUNE LOOP",
    "quality": "rare",
    "text": "RUNE LOOP|RING|REQUIRED LEVEL: 15|+1 TO MAXIMUM DAMAGE|3% LIFE STOLEN PER HIT|+5 TO STRENGTH|COLD RESIST +11%|FIRE RESIST +23%|9% BETTER CHANCE OF GETTING MAGIC ITEMS",
    "d2data":
    {
        "BaseItem":
        {
            "display_name": "Ring",
            "sets": ["angelic_halo", "cathans_seal"],
            "type": "ring",
            "uniques": ["nagelring", "manald_heal", "the_stone_of_jordan", "constricting_ring", "bulkathos_wedding_band", "dwarf_star", "raven_frost", "natures_peace", "wisp_projector", "carrion_wind"]
        },
        "Item": null,
        "ItemModifiers":
        {
            "maxdamage": [1],
            "lifesteal": [3],
            "str": [5],
            "res-cold": [11],
            "res-fire": [23],
            "mag%": [9]
        }
    },
    "nip":
    {
        "NTIPAliasType": 10,
        "NTIPAliasClassID": 522,
        "NTIPAliasClass": null,
        "NTIPAliasQuality": 6,
        "NTIPAliasStat":
        {
            "43": 11,
            "39": 23,
            "80": 9,
            "22": 1,
            "0": 5,
            "60": 3
        },
        "NTIPAliasFlag":
        {
            "0x10": true,
            "0x4000000": false
        }
    }
}""")


tests = [
    {
        "expression": "[name] == ring",
        "expected_result": True
    },

    {
        "expression": "[name] = ring",
        "expected_result": True
    },

    {
        "expression": "[name] = ring && [quality] == rare # [flag] != eth",
        "expected_result": True
    },
    
    {
        "expression": "[name] == ring & [quality] = rare",
        "expected_result": True
    },

    {
        "expression": "[name] = ring and [quality] = rare",
        "expected_result": True
    },


    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 11",
        "expected_result": True
    },



    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] >= 11",
        "expected_result": True
    },


    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] < 12",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist]  <= 11",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] != 12",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [fireresist] > 0 and [coldresist] > 0",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist]+[fireresist] == 34",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # ([coldresist]+[fireresist])*2 == 68",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # (([coldresist]+[fireresist])*2) / 4 == 17", # (68 * 2) / 4 = 17
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 11",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 11",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 11",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 11",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 11",
        "expected_result": True
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 11 and ethereal",
        "expected_result": True
    },


    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 12",
        "expected_result": False
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 12 // or [coldresist] == 11",
        "expected_result": False
    },
    
    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] == 11 and [coldresist] == 12",
        "expected_result": False
    },

    {
        "expression": "[name] == ring and [quality] = rare # [coldresist] < 11",
        "expected_result": False
    },

    {
        "expression": "[name] == ring and [quality] = rare # (([coldresist]+[fireresist])*2) / 47+[test]*5 == 5", # (68 * 2) / 4 = 17
        "expected_result": False
    }
]




expressions = preprocess_nip_file("kolton.nip")
for expression in expressions:
    try:
        eval(expression["pythonic_expression"])
    except (SyntaxError, TypeError, ValueError, AttributeError) as e:
        print(expression["nip_expression"] + "\n\n" + expression["pythonic_expression"] + "\n\n" + str(e))
        break


# for test in tests:

#     expression = test["expression"]
#     expected_result = test["expected_result"]
#     pythonic_expression = build_expression(expression)
#     assert eval(pythonic_expression.replace("\n", "")) == expected_result, expression
