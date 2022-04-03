from asyncore import write
import shelve
from bot_events import hook

# TODO: Make a gui that will read from the DB (the gui will be independent of a webserver)

def init_db():
    db = shelve.open('botty_db', writeback=True)
    entries = {"runs": [], "deaths": 0, "chickens": 0, "merc_deaths": 0, "failed_runs": 0,}
    for key in entries:
        if key not in db:
            db[key] = entries[key]

    db.close()

init_db()

def log_run(runs, deaths, chickens, merc_deaths):
    run = {
        # TODO: add items
        "runs": runs,
        "deaths": deaths, 
        "chickens": chickens, 
        "merc_deaths": merc_deaths, 
    }
    with shelve.open("botty_db", writeback=True) as db:
        db["runs"] = db["runs"] + [run]
        db["deaths"] += deaths
        db["chickens"] += chickens
        db["merc_deaths"] += merc_deaths


hook.Add("on_run", "BOTTY_DB_on_run", log_run)
