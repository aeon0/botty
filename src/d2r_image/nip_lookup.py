import re
from urllib import request


NTIP_ALIAS_CLASS_ID_BY_BASE = {}
NTIP_TYPE_ID_BY_TYPE = {}

class_id_regex = re.compile(r'NTIPAliasClassID\[\"([0-9a-zA-Z\']+)\"\] = ([0-9]+)')
type_id_regex = re.compile(r'NTIPAliasType\[\"([0-9a-zA-Z\']+)\"\] = ([0-9]+)')
# data = request.urlopen(url='https://raw.githubusercontent.com/blizzhackers/kolbot/master/d2bs/kolbot/libs/NTItemAlias.dbl').read().decode('utf-8')
data = open("assets/NTItemAlias.dbl", "r").read()
result = class_id_regex.findall(data)
if result:
    for class_id in result:
        NTIP_ALIAS_CLASS_ID_BY_BASE[class_id[0]] = class_id[1]
result = type_id_regex.findall(data)
if result:
    for type_id in result:
        NTIP_TYPE_ID_BY_TYPE[type_id[0]] = type_id[1]