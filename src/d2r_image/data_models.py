from enum import Enum
import numpy as np
import dataclasses
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

@dataclass
class OcrResult:
    text: str = None
    original_text: str = None
    #processed_img: np.ndarray = None
    word_confidences: list = None
    mean_confidence: float = None

    def __getitem__(self, key):
        return super().__getattribute__(key)

@dataclass
class ItemQuality(Enum):
    Gray = 'gray'
    Normal = 'normal'
    Magic = 'magic'
    Rare = 'rare'
    Set = 'set'
    Unique = 'unique'
    Crafted = 'crafted'
    Rune = 'rune'
    Runeword = 'runeword'
    Orange = 'orange'
    Superior = 'superior'
    LowQuality = 'lowquality'
    Cracked = 'lowquality'
    Crude = 'lowquality'
    Damaged = 'lowquality'


@dataclass
class ItemText:
    color: str = None
    quality: ItemQuality = None
    roi: list[int] = None
    img: np.ndarray = None
    clean_img: np.ndarray = None
    ocr_result: OcrResult = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


@dataclass
class ItemQualityKeyword(Enum):
    LowQuality = 'LOW QUALITY'
    Cracked = 'CRACKED'
    Crude = 'CRUDE'
    Damaged = 'DAMAGED'
    Superior = 'SUPERIOR'


@dataclass_json
@dataclass
class D2Item:
    boundingBox: dict
    name: str
    color: str | None
    quality: str | None
    type: str | None
    identified: bool
    amount: int | None
    baseItem: dict | None
    item: dict | None
    uniqueItems: list[dict] | None
    setItems: list[dict] | None
    itemModifiers: dict | None

    def __eq__(self, other):
        if self and not other:
            return False
        return self.boundingBox == other.boundingBox and\
            self.name == other.name and\
            self.color == other.color and\
            self.type == other.type and\
            self.identified == other.identified and\
            self.amount == other.amount and\
            self.baseItem == other.baseItem and\
            self.item == other.item and\
            self.uniqueItems == other.uniqueItems and\
            self.setItems == other.setItems and\
            self.itemModifiers == other.itemModifiers


@dataclass_json
@dataclass
class D2Data:
    BaseItem: dict
    Item: dict | None
    ItemModifiers: dict | None

    def __eq__(self, other):
        if self and not other:
            return False
        return self.to_json() == other.to_json()


@dataclass_json
@dataclass
class GroundItem:
    BoundingBox: dict = None
    BoundingBoxMonitor: dict = None
    Center: list[int] = None
    CenterMonitor: list[int] = None
    Distance: int = None
    Name: str = None
    Color: str = None
    Quality: str = None
    Text: str = None
    Amount: int | None = None
    BaseItem: dict = None
    Item: dict | None = None
    NTIPAliasType: list[str] = None
    NTIPAliasClassID: int = None
    NTIPAliasClass: int | None = None
    NTIPAliasQuality: int = None
    NTIPAliasFlag: dict = None
    ID: str = ""
    UID: str = ""

    def __eq__(self, other):
        if self and not other:
            return False
        return self.to_json() == other.to_json()

    def __getitem__(self, key):
        return super().__getattribute__(key)

    def as_dict(self):
        return {
            "Name": self.Name,
            "Color": self.Color,
            "Quality": self.Quality,
            "Text": self.Text,
            "Amount": self.Amount,
            "BaseItem": self.BaseItem,
            "Item": self.Item,
            "NTIPAliasType": self.NTIPAliasType,
            "NTIPAliasClassID": self.NTIPAliasClassID,
            "NTIPAliasClass": self.NTIPAliasClass,
            "NTIPAliasQuality": self.NTIPAliasQuality,
            "NTIPAliasFlag": self.NTIPAliasFlag
        }

@dataclass_json
@dataclass
class GroundItemList:
    items: list[GroundItem | None]


@dataclass_json
@dataclass
class HoveredItem:
    Name: str
    Quality: str
    Text: str
    BaseItem: dict
    Item: dict | None
    NTIPAliasIdName: str
    NTIPAliasType: list[str]
    NTIPAliasClassID: int
    NTIPAliasClass: int | None
    NTIPAliasQuality: int
    NTIPAliasStat: dict
    NTIPAliasFlag: dict

    def __eq__(self, other):
        if self and not other:
            return False
        return self.to_json() == other.to_json()

    def as_dict(self):
        return {
            'Name': self.Name,
            'Quality': self.Quality,
            'Text': self.Text,
            'BaseItem': self.BaseItem,
            'Item': self.Item,
            "NTIPAliasIdName": self.NTIPAliasIdName,
            'NTIPAliasType': self.NTIPAliasType,
            'NTIPAliasClassID': self.NTIPAliasClassID,
            'NTIPAliasClass': self.NTIPAliasClass,
            'NTIPAliasQuality': self.NTIPAliasQuality,
            'NTIPAliasStat': self.NTIPAliasStat,
            'NTIPAliasFlag': self.NTIPAliasFlag,
        }


@dataclass_json
@dataclass
class InventoryItem:
    boundingBox: dict
    type: str | None
    item: dict | None
    baseItems: list[dict] | None
    uniqueItems: list[dict] | None
    setItems: list[dict] | None

    def __eq__(self, other):
        if self and not other:
            return False
        return self.boundingBox == other.boundingBox and\
            self.type == other.type and\
            self.item == other.item and\
            self.baseItems == other.baseItems and\
            self.uniqueItems == other.uniqueItems and\
            self.setItems == other.setItems


@dataclass_json
@dataclass
class D2ItemList:
    items: list[D2Item | None]