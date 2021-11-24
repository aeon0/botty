import json
import os

def adjust_settings():
    # You might not belive it, but there are cases where users press f9 and just dont read any console output and think everything is done
    # so for now, removing this warning as it seems there has never been anybody actually backing up the original settings anyway...
    # print("Warning: This will overwrite some of your graphics and gameplay settings. D2R must not be running during this action! Continue with Enter...")
    # input()
    # Get D2r folder
    d2_saved_games = f"C:\\Users\\{os.getlogin()}\\Saved Games\\Diablo II Resurrected"
    if not os.path.exists(d2_saved_games):
        print(f"Your D2R Saved Games folder could not be found here: {d2_saved_games}, input the correct location:")
        d2_saved_games = input()
    if not os.path.exists(d2_saved_games):
        assert(f"Could not find D2R Saved Games at {d2_saved_games}")
    # adjust settings
    f = open(d2_saved_games + "\\Settings.json")
    curr_settings = json.load(f)
    f = open("assets/d2r_settings.json")
    new_settings = json.load(f)
    for key in new_settings:
        curr_settings[key] = new_settings[key]
    # write back to settings.json
    with open(d2_saved_games + "\\Settings.json", 'w') as outfile:
        json.dump(curr_settings, outfile)
    print("Changed settings succesfully. You can now start D2R and botty.")


if __name__ == "__main__":
    adjust_settings()
