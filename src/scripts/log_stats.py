import time
from bot_events import hook
from scripts.utils.misc import create_msg


start_time = time.time()
filename = f'stats_{time.strftime("%Y%m%d_%H%M%S")}.log'

def save_stats_to_file(instance, runs, deaths, chickens, merc_deaths, failed_runs, location, location_stats):
        msg = create_msg(instance, start_time, runs, deaths, chickens, merc_deaths, failed_runs, location, location_stats)
        msg += "\nItems:"
        for location in location_stats:
            if location == "totals":
                continue
            stats = location_stats[location]
            msg += f"\n  {location}:"
            for item_name in stats["items"]:
                msg += f"\n    {item_name}"

        with open(file=f"stats/{filename}", mode="w+", encoding="utf-8") as f:
            f.write(msg)

def log_stats(instance, runs, deaths, chickens, merc_deaths, failed_runs, location, location_stats):
    if runs > 0:
        save_stats_to_file(instance, runs, deaths, chickens, merc_deaths, failed_runs, location, location_stats)


hook.Add("on_run", "log_bot_stats", log_stats)