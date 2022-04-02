from bot_events import hook
from config import Config
from logger import Logger
import time
from inventory import belt

now = time.time()
last_rejuv = now
last_health = now
last_mana = now


def auto_pot_self(health_percentage, mana_percentage, img, instance):
    global last_rejuv
    global last_health
    global last_mana

    success_drink_rejuv = False
    last_drink = time.time() - last_rejuv
    if (health_percentage < Config().char["take_rejuv_potion_health"] and last_drink > 1) or \
        (mana_percentage < Config().char["take_rejuv_potion_mana"] and last_drink > 2):
        success_drink_rejuv = belt.drink_potion("rejuv", stats=[health_percentage, mana_percentage])
        instance._last_rejuv = time.time()
    # in case no rejuv was used, check for chicken, health pot and mana pot usage
    if not success_drink_rejuv:
        # check health
        last_drink = time.time() - last_health
        if health_percentage < Config().char["take_health_potion"] and last_drink > 3.5:
            belt.drink_potion("health", stats=[health_percentage, mana_percentage])
            last_health = time.time()
        # give the chicken a 6 sec delay to give time for a healing pot and avoid endless loop of chicken
        elif health_percentage < Config().char["chicken"] and (time.time() - start) > 6:
            Logger.warning(f"Trying to chicken, player HP {(health_percentage*100):.1f}%!")
            instance._do_chicken(img)
        # check mana
        last_drink = time.time() - last_mana
        if mana_percentage < Config().char["take_mana_potion"] and last_drink > 4:
            belt.drink_potion("mana", stats=[health_percentage, mana_percentage])
            last_mana = time.time()

last_merc_heal = 0
def auto_pot_merc(health_percentage, img, instance):
    global last_merc_heal
    last_drink = time.time() - last_merc_heal
    if health_percentage < Config().char["merc_chicken"]:
        Logger.warning(f"Trying to chicken, merc HP {(health_percentage*100):.1f}%!")
        instance._do_chicken(img)
    elif health_percentage < Config().char["heal_rejuv_merc"] and last_drink > 4.0:
        belt.drink_potion("rejuv", merc=True, stats=[health_percentage])
        last_merc_heal = time.time()
    elif health_percentage < Config().char["heal_merc"] and last_drink > 7.0:
        belt.drink_potion("health", merc=True, stats=[health_percentage])
        last_merc_heal = time.time()

hook.Add("on_self_health_update", "localplayer_auto_pot", auto_pot_self)
hook.Add("on_merc_health_update", "merc_auto_pot", auto_pot_merc)