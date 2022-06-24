GENERAL_SYNTAX_TESTS = [
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

SYNTAX_ERROR_TESTS = [
    # BNIP_0x1:Unknown token: 電:[sockets] 電話 1
    {
        "raw_expression": "[name] == ring # [sockets] 電話 1",
        "expected_code": "0x1",
    },
    # BNIP_0x2:Missing ] after keyword:[name == ring
    {
        "raw_expression": "[name == ring # [sockets] > 1",
        "expected_code": "0x2",
    },
    # BNIP_0x3:unexpected token on left of math operator:
    {
        "raw_expression": "[idname] + 3",
        "expected_code": "0x3",
    },
    # BNIP_0x4:unexpected token on right of math operator:
    {
        "raw_expression": "3 + [idname]",
        "expected_code": "0x4",
    },
    # BNIP_0x5, Invalid logical operator: '=': [sockets] = 1
    {
        "raw_expression": "[name] == ring # [sockets] = 1",
        "expected_code": "0x5",
    },
    # BNIP_0x6:unclosed parenthesis:
    {
        "raw_expression": "[name] == ring # (sockets == 4 || sockets == 3",
        "expected_code": "0x6",
    },
    # BNIP_0x7:unopened parenthesis
    {
        "raw_expression": "[name] == ring # sockets == 4 || sockets == 3)",
        "expected_code": "0x7",
    },
    # BNIP_0x8 -- I don't know how to make this one happen!
    # BNIP_0x9:Expected operator on right of number:
    {
        "raw_expression": "[name] == ring # 8 8",
        "expected_code": "0x9",
    },
    # BNIP_0x10:Expected token on left of logical operator
    {
        "raw_expression": "[Name] == ring # (< 8)",
        "expected_code": "0x10",
    },
    # BNIP_0x11:Expected token on right of logical operator
    {
        "raw_expression": "[idname] > ring",
        "expected_code": "0x11",
    },
    # BNIP_0x12 -- I don't know how to make this one happen!
    # BNIP_0x13:Invalid token 'xyaerrsddabd' in property section
    {
        "raw_expression": "[xyaerrsddabd] == ring",
        "expected_code": "0x13",
    },
    # BNIP_0x14:Invalid token 'xyaerrsddabd' in stats
    {
        "raw_expression": "[name] == ring # [xyaerrsddabd] >= 1",
        "expected_code": "0x14",
    },
    # BNIP_0x15 -- Impossible to force this error for now as maxquantity is cut out in prepare_bnip_expression()
    # BNIP_0x16:unexpected sectionand (#) at end of expression
    {
        "raw_expression": "[Name] == Lightgauntlets && [Quality] == Unique && [Flag] != Ethereal #",
        "expected_code": "0x16",
    },
    # BNIP_Ox17 -- I don't know how to make this one happen!
]