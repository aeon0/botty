from game_stats import GameStats
from transmute import Transmute
import threading
import keyboard
from ui.ui_manager import UiManager

if __name__ == "__main__":
    stats = GameStats()
    ui = UiManager(stats)
    cuber = Transmute(stats, ui)
    bot_thread = threading.Thread(target=cuber.run_transmutes, args=[True])
    bot_thread.daemon = True
    keyboard.add_hotkey("f11", lambda: bot_thread.start())
    keyboard.wait("f12")
