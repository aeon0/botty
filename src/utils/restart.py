import subprocess
import os, sys
import keyboard
from bot import Bot
from template_finder import TemplateFinder
from utils.misc import wait, set_d2r_always_on_top
from screen import Screen
from config import Config


def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def kill_game():
    while process_exists("D2R.exe"):
        os.system("taskkill /f /im  D2R.exe")
        wait(1.0, 1.5)

def restart_game(d2_path = None):
    if not d2_path:
        path = "C:\Program Files (x86)\Diablo II Resurrected\D2R.exe"
    else:
        path = d2_path
    kill_game()
    wait(1.0, 1.5)
    # This method should function similar to opening the exe via double-click
    os.startfile(path)
    wait(4.4, 5.5)
    for i in range(20):
        keyboard.send("space")
        wait(0.5, 1.0)
    success = False
    attempts = 0
    set_d2r_always_on_top()
    while not success:
        screen = Screen()
        success = screen.found_offsets        
        wait(0.5, 1.0)

    template_finder = TemplateFinder(screen)
    
    while not template_finder.search(Bot._MAIN_MENU_MARKERS,screen.grab(), best_match=True).valid:
        keyboard.send("space")
        wait(2.0, 4.0)
        attempts += 1
        if attempts >= 5:
            return False
    return True

# For testing 
if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = restart_game(sys.argv[1])
        print(result)
    else:
        result = restart_game()
        print(result)
