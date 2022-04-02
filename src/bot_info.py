from bot_events import hook
from config import Config

BOT_DATA = {
    "name": "", # name of the bot i.e botty..

    "char_type": "", # blizzsorc, hammerdin, etc..
    "char_health_percentage": 0,
    "char_mana_percentage": 0,
    "char_level": 0,
    "char_expereience": 0,

    "routes": [],
    "current_location": "",

    "items_found": [],

    "runs": 0,
    "deaths": 0,
    "chickens": 0,
    "merc_deaths": 0,
    "failed_runs": 0,
    "items": 0,

    "paused": False,
    "paused_for": 0,
    "running_for": 0,
}

def on_init(instance):
    BOT_DATA["name"] = Config().general['name']
    # BOT_DATA["char_type"] = instance._char
    BOT_DATA["routes"] = instance._do_runs
    print("INIT'd")

def on_run(runs, deaths, chickens, merc_deaths, items, failed_runs):
    BOT_DATA["runs"] = runs
    BOT_DATA["deaths"] = deaths
    BOT_DATA["chickens"] = chickens
    BOT_DATA["merc_deaths"] = merc_deaths
    BOT_DATA["failed_runs"] = failed_runs
    BOT_DATA["items"] = items


def update_pause(paused):
    BOT_DATA["paused"] = paused

i = 0
def update_pause_running_time():
    global i
    i+=1
    if i % 2 == 0: # Since the bot_loop is called every 0.5 seconds, and we want to update the time every second
        if BOT_DATA["paused"]:
            BOT_DATA["paused_for"] += 1
        else:
            BOT_DATA["running_for"] += 1

hook.Add("on_bot_init", "BOTDATA_init", on_init)

hook.Add("on_run", "BOTDATA_onrun", on_run)

hook.Add("on_pause", "BOTDATA_onpause", update_pause)
hook.Add("on_resume", "BOTDATA_onresume", update_pause)

hook.Add("bot_loop", "BOTDATA_update_pause_time", update_pause_running_time)
