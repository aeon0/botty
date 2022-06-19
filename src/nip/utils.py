from nip.UniqueAndSetData import UniqueAndSetData
from nip.lexer import NipSyntaxError

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
    raise NipSyntaxError("0x23", f"'{unique_or_set_name}' is not a valid unique or set")