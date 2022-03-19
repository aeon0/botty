from PIL import Image, ImageDraw, ImageFont
import argparse

parser = argparse.ArgumentParser(description="Generate item names/properties images to be used in pickit settings.")
parser.add_argument("-o", "--output", type=str, default="../../assets/item_properties", help="Output file name.", required=False)
parser.add_argument("-n", "--item_name", type=str, help="Item name (This will also be used inside pickit. No spaces.)", required=True)
parser.add_argument("-t", "--item_type", type=str, default="magic", help="Determines the text color & the image prefix file name. (item type matters.)", required=False, choices=[
    "gray"
    "normal",
    "magic",
    "rare",
    "unique",
    "set",
    "rune",
    "misc"
])

ITEM_COLORS = {
    "gray": (113,113,113),
    "white": (221,221,221),
    "magic": (123,123,236),
    "rare": (232,232,113),
    "unique": (194,178,129),
    "set": (4,241,4),
    "rune": (229,164,4),
    "misc": (229,164,4)
}

args = parser.parse_args()

font_size = 18
text = args.item_name

font = ImageFont.truetype('diablofont.otf', font_size)
text_size = font.getsize(text)

img = Image.new('RGBA', (text_size[0], text_size[1]), (2, 2, 2))

draw = ImageDraw.Draw(img)
font = ImageFont.truetype('diablofont.otf', font_size)

draw.text((0,0), text, font=font, fill=ITEM_COLORS[args.item_type])

img.save(f"{args.output}/{args.item_type}_{args.item_name}.png")