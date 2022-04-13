from inventory import belt
from pather import Location
import cv2
import time
import threading
import keyboard
from utils.custom_mouse import mouse
from utils.misc import wait, time_since
from logger import Logger
from screen import grab
import time
from config import Config
from inventory import common
from ui import view, meters
from ui_manager import ScreenObjects, is_visible

_pause_state = True

def get_pause_state():
	return _pause_state

def set_pause_state(state: bool):
	global _pause_state
	prev = get_pause_state()
	if prev != state:
		debug_str = "pausing" if state else "active"
		Logger.info(f"Health Manager is now {debug_str}")
		_pause_state = state

_run = False
_did_chicken = False
_callback = None
_last_chicken_screenshot = None
_count_panel_detects = 0
_hp = None
_mp = None
_merc_hp = None
_thread_id = None

# Gets the current HP as a percentage
def hp():
	return _hp

# Gets the current MP as a percentage
def mp():
	return _mp

# Gets the current HP of the merc as a percentage
def merc_hp():
	return _merc_hp

def is_in_game():
	return _hp is not None

def is_merc_alive():
	return _merc_hp is not None

# Updates the current HP, MP, and merc HP from a screen grab image
def update_values(img):
	global _hp, _mp, _merc_hp

	if is_visible(ScreenObjects.InGame, img):
		_hp = meters.get_health(img)
		_mp = meters.get_mana(img)

		if is_visible(ScreenObjects.MercIcon, img):
			_merc_hp = meters.get_merc_health(img)
		else:
			_merc_hp = None
	else:
		_hp = None
		_mp = None

def stop_monitor():
	global _run
	_run = False

def set_callback(callback):
	global _callback
	_callback = callback

def did_chicken():
	return _did_chicken

def reset_chicken_flag():
	global _did_chicken
	_did_chicken = False
	set_pause_state(True)

def _do_chicken(img):
	global _did_chicken, _callback

	if _callback is not None:
		_callback()
		_callback = None
	if Config().general["info_screenshots"]:
		_last_chicken_screenshot = "./info_screenshots/info_debug_chicken_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
		cv2.imwrite(_last_chicken_screenshot, img)
	# clean up key presses that might be pressed in the run_thread
	keyboard.release(Config().char["stand_still"])
	wait(0.02, 0.05)
	keyboard.release(Config().char["show_items"])
	wait(0.02, 0.05)
	mouse.release(button="left")
	wait(0.02, 0.05)
	mouse.release(button="right")
	time.sleep(0.01)
	view.save_and_exit()
	_did_chicken = True
	set_pause_state(True)

def start_health_manager():
	# Ensure this method runs in one thread only
	global _thread_id, _run, _did_chicken, _count_panel_detects

	if _thread_id is not None and _thread_id != threading.get_ident():
		Logger.info(f"Health monitor thread already running: {_thread_id}. Returning")
		return
	_thread_id = threading.get_ident()

	Logger.info("Start health monitoring")

	_run = True
	_did_chicken = False

	start = time.time()
	last_rejuv = time.time() - 100
	last_health = time.time() - 100
	last_mana = time.time() - 100
	last_merc_heal = time.time() - 100

	while _run:
		time.sleep(0.1)
		# Wait until the flag is reset by main.py
		if _did_chicken or get_pause_state(): continue
		img = grab()
		update_values(img)

		if is_in_game():
			# check rejuv
			success_drink_rejuv = False

			if (hp() < Config().char["take_rejuv_potion_health"] and time_since(last_rejuv) > 1) or \
			   (mp() < Config().char["take_rejuv_potion_mana"] and time_since(last_rejuv) > 2):
				success_drink_rejuv = belt.drink_potion("rejuv", stats=[hp(), mp()])
				last_rejuv = time.time()
			# in case no rejuv was used, check for chicken, health pot and mana pot usage
			if not success_drink_rejuv:
				# check health
				last_drink = time_since(last_health)
				if hp() < Config().char["take_health_potion"] and last_drink > 3.5:
					belt.drink_potion("health", stats=[hp(), mp()])
					last_health = time.time()
				# give the chicken a 6 sec delay to give time for a healing pot and avoid endless loop of chicken
				elif hp() < Config().char["chicken"] and (time.time() - start) > 6:
					Logger.warning(f"Trying to chicken, player HP {(hp()*100):.1f}%!")
					_do_chicken(img)
				# check mana
				last_drink = time.time() - last_mana
				if mp() < Config().char["take_mana_potion"] and last_drink > 4:
					belt.drink_potion("mana", stats=[hp(), mp()])
					last_mana = time.time()
			# check merc
			if is_merc_alive():
				last_drink = time.time() - last_merc_heal
				if merc_hp() < Config().char["merc_chicken"]:
					Logger.warning(f"Trying to chicken, merc HP {(merc_hp()*100):.1f}%!")
					_do_chicken(img)
				if merc_hp() < Config().char["heal_rejuv_merc"] and last_drink > 4.0:
					belt.drink_potion("rejuv", merc=True, stats=[merc_hp()])
					last_merc_heal = time.time()
				elif merc_hp() < Config().char["heal_merc"] and last_drink > 7.0:
					belt.drink_potion("health", merc=True, stats=[merc_hp()])
					last_merc_heal = time.time()
			if is_visible(ScreenObjects.LeftPanel, img) or is_visible(ScreenObjects.RightPanel, img):
				Logger.warning(f"Found an open inventory / quest / skill / stats page. Close it.")
				_count_panel_detects += 1
				if _count_panel_detects >= 2:
					_count_panel_detects = 0
					Logger.warning(f"Found an open inventory / quest / skill / stats page again. Chicken to dismiss.")
					_do_chicken(img)
				common.close()
	Logger.debug("Stop health monitoring")


# Testing: Start dying or losing mana and see if it works
if __name__ == "__main__":
	import keyboard
	import os
	keyboard.add_hotkey('f12', lambda: Logger.info('Exit Health Manager') or os._exit(1))
	set_pause_state(True)
	Logger.info("Press f12 to exit health manager")
	health_monitor_thread = threading.Thread(target=start_health_manager)
	health_monitor_thread.start()
	while 1:
		if did_chicken():
			stop_monitor()
			health_monitor_thread.join()
			break
		wait(0.5)
