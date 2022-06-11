
from dataclasses import dataclass

@dataclass
class ExpressionTest:
    basename: str = None
    expression: str = None
    transpiled: str = None
    read_json: dict = None
    keep_or_pick_expected: bool = False
    id_expected: bool = False
