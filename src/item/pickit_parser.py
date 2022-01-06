import json
#import parse

class PickitParse:
    def __init__(self):

        self.all_colors = ["white", "gray", "green", "gold", "blue", "orange", "yellow"]
        self.quality_to_color = {
            "normal": ["white", "gray"],
            "superior": ["gray"],
            "set": ["green"],
            "unique": ["gold"],
            "magic": ["blue"],
            "special": ["orange"],
            "rare": ["yellow"]
        }

        with open("../config/pickit_config.json", "r",encoding = 'utf-8') as f:
            self.f_pickit = json.loads(json.dumps(json.load(f)).upper())
        with open("refs/set_items.json", "r",encoding = 'utf-8') as f:
            self.f_set_items = json.loads(json.dumps(json.load(f)).upper())
        with open("refs/unique_items.json", "r",encoding = 'utf-8') as f:
            self.f_unique_items = json.loads(json.dumps(json.load(f)).upper())
        with open("refs/codes.json", "r",encoding = 'utf-8') as f:
            self.f_codes = json.loads(json.dumps(json.load(f)).upper())
        with open("refs/types.json", "r",encoding = 'utf-8') as f:
            self.f_types = json.loads(json.dumps(json.load(f)).upper())
        with open("refs/armor.json", "r",encoding = 'utf-8') as f:
            self.f_armor = json.loads(json.dumps(json.load(f)).upper())
        with open("refs/weapons.json", "r",encoding = 'utf-8') as f:
            self.f_weapons = json.loads(json.dumps(json.load(f)).upper())

        self.drop_list = self.gen_drop_list()

    def convert_code_name(self, inp_str: str, in_type: str = "name", out_type: str = "code"):
        for key in self.f_codes:
            if inp_str == self.f_codes[key][in_type]:
                return self.f_codes[key][out_type]
        return False

    def get_base_name_and_color(self, inp_str: str, inp_type: str):
        items=[]
        if inp_type == "quality":
            for key in self.f_codes:
                if self.f_codes[key]["quality"] == inp_str:
                    # convert "paf" code to "name" -> "vortex_shield"
                    item_name = self.convert_code_name(key, "code", "name")
                    item_display_name = self.convert_code_name(key, "code", "display_name")
                    if inp_str == "set":
                        file = self.f_set_items
                    elif inp_str == "unique":
                        file = self.f_unique_items
                    else:
                        items.append(item_display_name)
                        continue
                    if item_name in file:
                        if "base" in file[item_name]:
                            items.append(self.convert_code_name(file[item_name]["base"], "name", "display_name"))
            return items, self.quality_to_color[inp_str]
        if inp_type == "type":
            colors=[]
            for key in self.f_codes:
                if self.f_codes[key]["display_name"] == inp_str or self.f_codes[key]["name"] == inp_str:
                    type_name = self.f_codes[key]["name"]
                    break
            for item in self.f_types[type_name]["items"]:
                item_display_name = self.convert_code_name(item, "name", "display_name")
                items.append(item_display_name)
                item_code = self.convert_code_name(item, "name", "code")
                item_quality = self.f_codes[item_code]["quality"]
                if "special" in item_quality:
                    item_colors = self.quality_to_color[item_quality]
                    for item_color in item_colors:
                        if item_color not in colors:
                            colors.append(item_color)
                else:
                    colors = self.all_colors()
            return items, list(set(colors))
        else:
            item_display_name = self.convert_code_name(inp_str, inp_type, "display_name")
            item_code = self.convert_code_name(inp_str, inp_type, "code")
            item_name = self.convert_code_name(inp_str, inp_type, "name")
            # print(f"disp_name: {item_display_name}, code: {item_code}, name: {item_name}")
            colors = self.quality_to_color[self.f_codes[item_code]["quality"]]
            for file in [ self.f_unique_items, self.f_set_items ]:
                if item_name in file:
                    if "base" in file[item_name]:
                        return [self.convert_code_name(file[item_name]["base"], "name", "display_name")], colors
            return [item_display_name], colors
        return False

    def filter_item_by(self, filter_type: str = "type", item: dict = None, current_drop_list: list = [], current_colors: list = []):
        if filter_type in item:
            base_names, result_colors = self.get_base_name_and_color(item[filter_type],filter_type)
            if current_drop_list:
                current_drop_list = [x for x in current_drop_list if x in set(base_names)]
                current_colors = [x for x in current_colors if x in set(result_colors)]
            else:
                current_drop_list = base_names
                current_colors = result_colors
        return current_drop_list, current_colors


    def gen_drop_list(self):
        # generate a list of all the item names and colors that should be picked up

        # item and type properties:
        # name (key name): auric_shields, lacquered_plate, tal_rashas_guardianship
        # display_name: Auric Shields, Lacquered Plate, Tal-Rasha's Guardianship
        # type: auric_shields, armor, __
        # base: ___, ____, lacquered_plate
        # item_class: ____, Elite, ____
        # props: [{ "max": 5, "min": 2, "par": 0, "prop": "sock" }, ...]
        # set: "Tal Rasha's Wrappings"
        # hands: one/two/both

        full_drop_list = []
        for item in self.f_pickit["items"]:
            current_drop_list = []
            current_colors = []
        # 1. handle "name"
            current_drop_list, current_colors = self.filter_item_by("name", item, current_drop_list, current_colors)
        # 2. handle "display_name"
            current_drop_list, current_colors = self.filter_item_by("display_name", item, current_drop_list, current_colors)
        # 3. handle "type"
            current_drop_list, current_colors = self.filter_item_by("type", item, current_drop_list, current_colors)
        # 4. handle "quality"
            current_drop_list, current_colors = self.filter_item_by("quality", item, current_drop_list, current_colors)
        # 5. handle "item_class"
            if "item_class" in item:
                sub_list = []
                for file in [ self.f_armor, self.f_weapons ]:
                    for key in file:
                        if "item_class" in file[key] and file[key]["item_class"] == item["item_class"]:
                            sub_list.append(self.convert_code_name(key, "name", "display_name"))
                sub_colors = self.all_colors()
                if current_drop_list:
                    current_drop_list = [x for x in current_drop_list if x in set(sub_list)]
                    current_colors = current_colors
                else:
                    current_drop_list = sub_list
                    current_colors = sub_colors
        # 6. handle "props" ethereal and socketed
            sub_colors = self.all_colors()
            eth = -1
            soc = -1
            if "props" in item:
                for prop in item["props"]:
                    #print(prop)
                    if "name" in prop:
                        if prop["name"] == "ethereal":
                            eth = 1
                            if "arg1" in prop:
                                if int(prop["arg1"]) == 0:
                                    eth = 0
                        elif prop["name"] == "socketed":
                            soc = 1
                            if "arg1" in prop:
                                if int(prop["arg1"]) == 0:
                                    soc = 0
            if (soc == -1 and eth == 0) or (soc == 0 and eth == -1):
                sub_colors.remove("gray")
            if (soc == 1) or (eth == 1):
                sub_colors.remove("white")
            current_colors = [x for x in current_colors if x in set(sub_colors)]

            for drop in current_drop_list:
                for col in current_colors:
                    full_drop_list.append({"name": drop, "color": col})
        return full_drop_list

if __name__ == "__main__":
    exit()