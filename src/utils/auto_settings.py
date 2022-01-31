import json
import os
import shutil

from config import Config
from mss import mss
from utils.misc import close_down_d2


def get_d2r_folder() -> str:
    """
    Get D2r folder
    try to find pre-set D2r folder
    :param config: the general config possibly containing 'saved_games_folder'
    :return: the D2r folder full path
    """
    config = Config()
    d2_saved_games = config.general["saved_games_folder"]
    if not d2_saved_games:
        # assign default value for en-us Windows users
        d2_saved_games = f"C:\\Users\\{os.getlogin()}\\Saved Games\\Diablo II Resurrected"
    if not os.path.exists(d2_saved_games):
        print(f"Your D2R Saved Games folder could not be found here: {d2_saved_games}, input the correct location:")
        d2_saved_games = input()
    if not os.path.exists(d2_saved_games):
        assert(f"Could not find D2R Saved Games at {d2_saved_games}")
    return d2_saved_games


def backup_settings():
    d2_saved_games = get_d2r_folder()
    if os.path.exists(d2_saved_games + "\\Settings_backup.json"):
        r = input("Backup file already exist, are you sure you want to overwrite it? [y] to confirm")
        if r == 'y':
            shutil.copyfile(d2_saved_games + "\\Settings.json", d2_saved_games + "\\Settings_backup.json")
            print("Settings backed up successfully.")
    else:
        shutil.copyfile(d2_saved_games + "\\Settings.json", d2_saved_games + "\\Settings_backup.json")
        print("Settings backed up successfully.")


def restore_settings_from_backup():
    d2_saved_games = get_d2r_folder()
    if os.path.exists(d2_saved_games + "\\Settings_backup.json"):
        close_down_d2()
        shutil.copyfile(d2_saved_games + "\\Settings_backup.json", d2_saved_games + "\\Settings.json")
        print("Settings restored successfully.")
    else:
        print("No backup was found, couldn't restore settings.")

def adjust_settings():
    close_down_d2()
    # find monitor res
    sct = mss()
    monitor_idx = 1
    if len(sct.monitors) == 1:
        print("How do you not have a monitor connected?!")
        os._exit(1)
    d2_saved_games = get_d2r_folder()
    # adjust settings
    f = open(d2_saved_games + "\\Settings.json")
    curr_settings = json.load(f)
    f = open("assets/d2r_settings.json")
    new_settings = json.load(f)
    for key in new_settings:
        curr_settings[key] = new_settings[key]
    # In case monitor res is at 720p, force fullscreen
    if sct.monitors[monitor_idx]['width'] == 1280 and sct.monitors[monitor_idx]['height'] == 720:
        print(f"Detected 720p Monitor res. Forcing fullscreen mode.")
        curr_settings["Window Mode"] = 1
    # write back to settings.json
    with open(d2_saved_games + "\\Settings.json", 'w') as outfile:
        json.dump(curr_settings, outfile)
    print("Adapted settings succesfully. You can now restart D2R.")

def check_settings() -> dict:
    d2_saved_games = get_d2r_folder()
    # adjust settings
    f = open(d2_saved_games + "\\Settings.json")
    curr_settings = json.load(f)
    f = open("assets/d2r_settings.json")
    new_settings = json.load(f)
    diff_settings = {}
    for key in new_settings:
        if key != "Window Mode" and curr_settings[key] != new_settings[key]:
            diff_settings[key] = [curr_settings[key], new_settings[key]]
    return diff_settings

if __name__ == "__main__":
    adjust_settings()
