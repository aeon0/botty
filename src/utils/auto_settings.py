import json
import os
import shutil

from config import Config
from mss import mss
from utils.misc import close_down_bnet_launcher, close_down_d2


def get_d2r_folder() -> str:
    """
    Get D2r folder
    try to find pre-set D2r folder
    :param config: the general config possibly containing 'saved_games_folder'
    :return: the D2r folder full path
    """
    d2_saved_games = Config().general["saved_games_folder"]
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
    backup_file = f"{d2_saved_games}/Settings_backup.json"
    current_file = f"{d2_saved_games}/Settings.json"
    if os.path.exists(backup_file):
        r = input("D2R settings backup already exists, are you sure you want to overwrite it? [y] to confirm")
        if not r == 'y':
            return
    shutil.copyfile(current_file, backup_file)
    print("D2R settings backed up successfully.")

    backup_file = f"{d2_saved_games}/launch_options_backup.txt"
    current_file = f"{os.getenv('APPDATA')}/Battle.net/Battle.net.config"
    if os.path.exists(backup_file):
        r = input("D2R launch options backup already exists, are you sure you want to overwrite it? [y] to confirm")
        if not r == 'y':
            return
    f = open(current_file)
    curr_settings = json.load(f)
    launch_options = curr_settings["Games"]["osi"]["AdditionalLaunchArguments"]
    with open(backup_file, 'w') as f:
        f.write(launch_options)
    print("D2R launch options backed up successfully.")

def restore_settings_from_backup():
    d2_saved_games = get_d2r_folder()
    backup_file = f"{d2_saved_games}/Settings_backup.json"
    current_file = f"{d2_saved_games}/Settings.json"
    if not os.path.exists(backup_file):
        print("No D2R settings backup file was found, couldn't restore.")
        return
    close_down_d2()
    shutil.copyfile(backup_file, current_file)
    print("D2R settings restored successfully.")

    backup_file = f"{d2_saved_games}/launch_options_backup.txt"
    current_file = f"{os.getenv('APPDATA')}/Battle.net/Battle.net.config"
    if not os.path.exists(backup_file):
        print("No D2R launch options backup file was found, couldn't restore.")
        return
    with open(backup_file, 'r') as f:
        launch_options = f.read().strip()
    set_launch_settings(launch_options)
    print("D2R launch options restored successfully.")

def set_launch_settings(launch_options):
    close_down_bnet_launcher()
    f = open(f"{os.getenv('APPDATA')}/Battle.net/Battle.net.config")
    curr_settings = json.load(f)
    curr_settings["Games"]["osi"]["AdditionalLaunchArguments"] = launch_options
    with open(f"{os.getenv('APPDATA')}/Battle.net/Battle.net.config", 'w') as outfile:
        json.dump(curr_settings, outfile, indent=4)

def copy_mod_files(): 
    new_path = os.path.join(Config().general['d2r_path'], "mods\\botty")
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    try:
        shutil.rmtree(new_path)
        shutil.copytree("assets/mods/botty", new_path)
    except OSError as error:
        print(error)

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
    if Config().advanced_options["launch_options"]:
        set_launch_settings(Config().advanced_options["launch_options"])
        copy_mod_files()
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
    copy_mod_files()
