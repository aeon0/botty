from ui_manager import UiManager
from item_finder import ItemFinder
from template_finder import TemplateFinder
from config import Config
from screen import Screen
from char.sorceress import Sorceress
from char.hammerdin import Hammerdin


config = Config()
screen = Screen(config.general["monitor"])
t_finder = TemplateFinder(screen)
ui_manager = UiManager(screen, t_finder)
item_finder = ItemFinder()
hdin = Hammerdin(config.hammerdin, config.char, screen, t_finder, item_finder, ui_manager)
sorc = Sorceress(config.sorceress, config.char, screen, t_finder, item_finder, ui_manager)
hdin.pick_up_item("test")
sorc.pick_up_item("test")
