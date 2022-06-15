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
    # NIP_0x1:Unknown token: 電:[sockets] 電話 1
    {
        "raw_expression": "[name] == ring # [sockets] 電話 1",
        "expected_code": "0x1",
    },
    # NIP_0x2:Missing ] after keyword:[name == ring
    {
        "raw_expression": "[name == ring # [sockets] > 1",
        "expected_code": "0x2",
    },
    # NIP_0x3:unexpected token on left of math operator:
    {
        "raw_expression": "[idname] + 3",
        "expected_code": "0x3",
    },
    # NIP_0x4:unexpected token on right of math operator:

    # NIP_0x5, Invalid logical operator: '=': [sockets] = 1
    {
        "raw_expression": "[name] == ring # [sockets] = 1",
        "expected_code": "0x5",
    },
    # NIP_0x12:Invalid token 'xyaerrsddabd' in property section
    {
        "raw_expression": "[xyaerrsddabd] == ring",
        "expected_code": "0x12",
    },
    # NIP_0x13:Invalid token 'xyaerrsddabd' in stats
    {
        "raw_expression": "[name] == ring # [xyaerrsddabd] >= 1",
        "expected_code": "0x13",
    },
]