from PIL import Image, ImageDraw, ImageFont
import argparse

parser = argparse.ArgumentParser(description="Generate item properties images to be used in pickit settings.")
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
    "gray": (92,92,93),
    "normal": (194,194,195),
    "magic": (106,107,207),
    "rare": (207,207,98),
    "unique": (162,151,108),
    "set": (0,204,1),
    "rune": (199,142,1),
    "misc": (199,142,1)
}

args = parser.parse_args()

font_size = 16
text = args.item_name

font = ImageFont.truetype('diablofont.otf', font_size)
text_size = font.getsize(text)

img = Image.new('RGBA', (text_size[0], text_size[1]), (2, 2, 2))

draw = ImageDraw.Draw(img)
font = ImageFont.truetype('diablofont.otf', font_size)

draw.text((0,0), text, font=font, fill=ITEM_COLORS[args.item_type])

img.save(f"{args.output}/{args.item_type}_{args.item_name}.png")