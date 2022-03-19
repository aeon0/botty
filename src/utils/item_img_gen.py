from PIL import Image, ImageDraw, ImageFont
import argparse

parser = argparse.ArgumentParser(description="Generate item names/properties images to be used in pickit settings.")
parser.add_argument("-o", "--output_dir", type=str, default="../../assets/items", help="Output directory.", required=False)
parser.add_argument("-n", "--item_name", type=str, help="Item name (will be the file name if no file name provided.)", required=True)
parser.add_argument("-f", "--file_name", type=str, help="If you want to name the file specifically so when you use it in pickit, it's more descriptive.", required=False)
parser.add_argument("-t", "--item_type", type=str, default="magic", help="Determines the text color & the image prefix file name. (item type matters.)", required=False, choices=[
    "gray"
    "white",
    "magic",
    "rare",
    "unique",
    "set",
    "rune",
    "misc"
])
args = parser.parse_args()

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


font_size = 19
text = args.item_name

font = ImageFont.truetype('diablofont.otf', font_size)
text_size = font.getsize(text)

img = Image.new('RGBA', (text_size[0], text_size[1]), (2, 2, 2))

draw = ImageDraw.Draw(img)
font = ImageFont.truetype('diablofont.otf', font_size)
draw.text((0,0), text, font=font, fill=ITEM_COLORS[args.item_type])

file_name = args.file_name.replace(" ", "_") if args.file_name else args.item_name.replace(" ", "_")

img.save(f"{args.output_dir}/{args.item_type}_{file_name}.png")

print(f"saved {args.output_dir}\\{args.item_type}_{file_name}.png")