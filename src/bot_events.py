from logger import Logger

callbacks = {
    "on_bot_init": {},

    "on_create_game": {},
    "on_end_game": {},

    "on_run_pindle": {},
    "on_run_shenk": {},
    "on_run_trav": {},
    "on_run_nihlathak": {},
    "on_run_arcane": {},
    "on_run_diablo": {},
    "on_run_end": {},

    "on_pause": {},
    "on_resume": {},

    "on_item_keep": {},
    "on_run": {},
    "on_death": {},
    "on_chicken": {},
    "on_merc_death": {},
    "on_failed_run": {},

    "on_health_mana_update": {},
}

def callback_register(callback_type, unique_identifier, callback, *args, instance=None):
    def cb(*args, **kwargs):
        return callback(*args, **kwargs)
    callbacks[callback_type][unique_identifier] = cb

def callback_unregister(callback_type, unique_identifier):
    del callbacks[callback_type][unique_identifier]

def callback_exists(callback_type, unique_identifier):
    return unique_identifier in callbacks[callback_type]
    
def callback_call(callback_type, *args, **kwargs):
    for callback in callbacks[callback_type].values():
        callback(*args, **kwargs)

# callback_register("on_bot_init", lambda: print("on_bot_init"))
# callback_register("on_game_create", lambda: print("on_game_create"))
# callback_register("on_game_end", lambda: print("on_game_end"))
# callback_register("on_pindle_run", lambda: print("on_pindle_run"))
# callback_register("on_shenk_run", lambda: print("on_shenk_run"))
# callback_register("on_trav_run", lambda: print("on_trav_run"))
# callback_register("on_nihlathak_run", lambda: print("on_nihlathak_run"))
# callback_register("on_arcane_run", lambda: print("on_arcane_run"))
# callback_register("on_diablo_run", lambda: print("on_diablo_run"))
# callback_register("on_run_end", lambda: print("on_run_end"))
# callback_register("on_pause", lambda: print("on_pause"))
# callback_register("on_resume", lambda: print("on_resume"))
# callback_register("on_item_keep", lambda: print("on_item_keep"))
# callback_register("on_run", lambda: print("on_run"))
# callback_register("on_death", lambda: print("on_death"))
# callback_register("on_chicken", lambda: print("on_chicken"))
# callback_register("on_merc_death", lambda: print("on_merc_death"))
# callback_register("on_failed_run", lambda: print("on_failed_run"))

