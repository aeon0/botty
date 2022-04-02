import time
from utils.misc import hms
from config import Config
from beautifultable import BeautifulTable


def create_msg(instance, start_time, runs, deaths, chickens, merc_deaths, failed_runs, location, location_stats):
        elapsed_time = time.time() - start_time
        elapsed_time_str = hms(elapsed_time)
        avg_length_str = "n/a"
        good_games_count = runs - failed_runs
        good_games_time = elapsed_time - instance._failed_game_time

        if good_games_count == 0:
            good_games_count = 1

        avg_length = good_games_time / float(good_games_count)
        avg_length_str = hms(avg_length)

        # curr_lvl = get_level(self._current_lvl)
        # exp_gained = self._current_exp - curr_lvl['exp']
        # per_to_lvl = exp_gained / curr_lvl["xp_to_next"]
        # gained_exp = self._current_exp - self._starting_exp
        # exp_per_second = gained_exp / good_games_time
        # exp_per_hour = round(exp_per_second * 3600, 1)
        # exp_per_game = round(gained_exp / float(good_games_count), 1)
        # exp_needed = curr_lvl['xp_to_next'] - exp_gained
        # time_to_lvl = exp_needed / exp_per_second
        # games_to_lvl = exp_needed / exp_per_game

        msg = f'\nSession length: {elapsed_time_str}'
        msg += f'\nGames: {runs}'
        msg += f'\nAvg Game Length: {avg_length_str}'
        # msg += f'\nCurrent Level: {curr_lvl["lvl"]}'
        # msg += f'\nPercent to Level: {math.ceil(per_to_lvl*100)}%'
        # msg += f'\nXP Gained: {gained_exp:,}'
        # msg += f'\nXP Per Hour: {exp_per_hour:,}'
        # msg += f'\nXP Per Game: {exp_per_game:,}'
        # msg += f'\nTime Needed To Level: {hms(time_to_lvl)}'
        # msg += f'\nGames Needed To Level: {math.ceil(games_to_lvl):,}'

        table = BeautifulTable()
        table.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
        for location in location_stats:
            if location == "totals":
                continue
            stats = location_stats[location]
            table.rows.append([location, len(stats["items"]), stats["chickens"], stats["deaths"], stats["merc_deaths"], stats["failed_runs"]])

        table.rows.append([
            "T" if Config().general['discord_status_condensed'] else "Total",
            location_stats["totals"]["items"],
            location_stats["totals"]["chickens"],
            location_stats["totals"]["deaths"],
            location_stats["totals"]["merc_deaths"],
            location_stats["totals"]["failed_runs"]
        ])

        if Config().general['discord_status_condensed']:
            table.columns.header = ["Run", "I", "C", "D", "MD", "F"]
        else:
            table.columns.header = ["Run", "Items", "Chicken", "Death", "Merc Death", "Failed Runs"]

        msg += f"\n{str(table)}\n"
        return msg