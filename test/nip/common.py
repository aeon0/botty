from dataclasses import dataclass

@dataclass
class ExpressionTest:
    basename: str = None
    expression: str = None
    transpiled: str = None
    read_json: dict = None
    pick_expected: bool = False
    keep_expected: bool = False
    id_expected: bool = False

# for when json.dumps() fails...
def pretty_dict(dictionary):

    def _nested(obj, level=1):
        indentation_values = "\t" * level
        indentation_braces = "\t" * (level - 1)
        if isinstance(obj, dict):
            return "{\n%(body)s%(indent_braces)s}" % {
                "body": "".join("%(indent_values)s\'%(key)s\': %(value)s,\n" % {
                    "key": str(key),
                    "value": _nested(value, level + 1),
                    "indent_values": indentation_values
                } for key, value in obj.items()),
                "indent_braces": indentation_braces
            }
        if isinstance(obj, list):
            return "[\n%(body)s\n%(indent_braces)s]" % {
                "body": "".join("%(indent_values)s%(value)s,\n" % {
                    "value": _nested(value, level + 1),
                    "indent_values": indentation_values
                } for value in obj),
                "indent_braces": indentation_braces
            }
        else:
            return "\'%(value)s\'" % {"value": str(obj)}

    dict_text = _nested(dictionary)
    return dict_text