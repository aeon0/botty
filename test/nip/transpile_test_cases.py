items = [
    { # Magic ring
        "Name": "BAHAMUT'S RING OF FORTUNE",
        "Quality": "magic",
        "Text": "BAHAMUT'S RING OF FORTUNE|REQUIRED LEVEL: 37|+106 TO MANA|25% BETTER CHANCE OF GETTING MAGIC ITEMS",
        "BaseItem": {
            "DisplayName": "Burning Essence of Terror",
            "NTIPAliasClassID": 522,
            "NTIPAliasType": 39,
            "dimensions": [
                1,
                1
            ]
        },
        "Item": 0,
        "NTIPAliasIdName": "BAHAMUTSRINGOFFORTUNE",
        "NTIPAliasType": 39,
        "NTIPAliasClassID": 522,
        "NTIPAliasClass": 0,
        "NTIPAliasQuality": 4,
        "NTIPAliasStat": {
            "80": 25,
            "9": 106
        },
        "NTIPAliasFlag": {
            "0x10": True,
            "0x400000": False,
            "0x4000000": False
        }
    }
]

general_syntax_tests = [
    {
        "raw_expression": "[name] == ring",
        "should_fail": False,
    },
    {
        "raw_expression": "[name] = ring",
        "should_fail": True,
    },

    {
        "raw_expression": "[name] > ring",
        "should_fail": False,
    },

    {
        "raw_expression": "[name] < ring",
        "should_fail": False,
    },


    {
        "raw_expression": "[name] >= ring",
        "should_fail": False
    },
    {
        "raw_expression": "[name] <= ring",
        "should_fail": False,
    },


    {
        "raw_expression": "[name] >== ring",
        "should_fail": True,
    },
    {
        "raw_expression": "[name] ==> ring",
        "should_fail": True,
    },

    {
        "raw_expression": "[name] != ring",
        "should_fail": False,
    },
    {
        "raw_expression": "[name] =! ring",
        "should_fail": True,
    }
]


section_syntax_tests = [
    {
        "raw_expression": "[name] == ring",
        "should_fail": False,
    },

    {
        "raw_expression": "[name] == ring && [quality] == unique",
        "should_fail": False,
    },

    {
        "raw_expression": "[name] == ring # [quality] == unique",
        "should_fail": True
    },

]


transpile_tests = [
        {
            "raw_expression": "[name] == ring && [quality] == rare",
            "transpiled_expression": "(int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['ring']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['rare']))",
        },
        {
            "raw_expression": "[type] == ring && [quality] == rare",
            "transpiled_expression": "(int(item_data['NTIPAliasType']))==(int(NTIPAliasType['ring']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['rare']))",
        },  
    
        {
            "raw_expression": "[name] == ring && [quality] == rare # [strength] == 5",
            "transpiled_expression": "(int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['ring']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['rare']))and(int(item_data['NTIPAliasStat'].get('0', -1)))==(5.0)",
        },
        {
            "raw_expression": "[type] == ring && [quality] == rare # [strength] == 5",
            "transpiled_expression": "(int(item_data['NTIPAliasType']))==(int(NTIPAliasType['ring']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['rare']))and(int(item_data['NTIPAliasStat'].get('0', -1)))==(5.0)",
        },

        {
            "raw_expression": "[name] == ring && [quality] == rare # [strength] == 5 && [sockets] == 2",
            "transpiled_expression": "(int(item_data['NTIPAliasClassID']))==(int(NTIPAliasClassID['ring']))and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['rare']))and(int(item_data['NTIPAliasStat'].get('0', -1)))==(5.0)and(int(item_data['NTIPAliasStat'].get('194', -1)))==(2.0)",
        },

        {
            "raw_expression": "[idname] == thestoneofjordan",
            "transpiled_expression": "(str(item_data['NTIPAliasIdName']).lower())==(str('thestoneofjordan').lower())",
        },

        {
            "raw_expression": "[idname] == thestoneofjordan && [quality] == unique",
            "transpiled_expression": "(str(item_data['NTIPAliasIdName']).lower())==(str('thestoneofjordan').lower())and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['unique']))",
        },

        {
            "raw_expression": "[idname] == thestoneofjordan && [quality] == unique # [strength] == 5",
            "transpiled_expression": "(str(item_data['NTIPAliasIdName']).lower())==(str('thestoneofjordan').lower())and(int(item_data['NTIPAliasQuality']))==(int(NTIPAliasQuality['unique']))and(int(item_data['NTIPAliasStat'].get('0', -1)))==(5.0)",
        },
        

    ]