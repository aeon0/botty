
from dataclasses import dataclass

@dataclass
class ExpressionTest():
    basename: str = None
    expression: str = None
    transpiled: str = None
    read_json: dict = None
    expected_result: bool = False