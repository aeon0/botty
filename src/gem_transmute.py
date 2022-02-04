from screen import Screen
from game_stats import GameStats
from template_finder import TemplateFinder
from transmute import Transmute
import threading
import keyboard
from ui.ui_manager import UiManager

if __name__ == "__main__":
    s = Screen()
    finder = TemplateFinder(s)
    stats = GameStats()
    ui = UiManager(s, finder, stats)
    cuber = Transmute(s, finder, stats, ui)
    bot_thread = threading.Thread(target=cuber.run_transmutes, args=[True])
    bot_thread.daemon = True
    keyboard.add_hotkey("f11", lambda: bot_thread.start())
    keyboard.wait("f12")
