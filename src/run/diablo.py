import cv2
import time, random
import keyboard
from automap_finder import toggle_automap
from char.i_char import IChar
from config import Config
from health_manager import set_pause_state
from logger import Logger
from pather import Location, Pather
from item.pickit import PickIt
import template_finder
from town.town_manager import TownManager, A4
from utils.misc import cut_roi, wait
from utils.custom_mouse import mouse
from screen import convert_abs_to_monitor, convert_abs_to_screen, grab
from ui_manager import detect_screen_object, ScreenObjects, is_visible #cstownvisits
from ui import skills, loading, waypoint, meters, view, character_select, main_menu #cstownvisits
from inventory import belt, personal, common
from item import consumables #cstownvisits
from game_stats import GameStats #cstownvisits
from d2r_image import processing as d2r_image  #loot check dia (diff)

class Diablo:

    name = "run_diablo"

    def __init__(
        self,
        pather: Pather,
        town_manager: TownManager,
        char: IChar,
        pickit: PickIt,
        runs: list[str],
        game_stats: GameStats
    ):
        self._game_stats = game_stats
        self._pather = pather
        self._town_manager = town_manager
        self._char = char
        self._pickit = pickit
        self._picked_up_items = False
        self.used_tps = 0
        self._curr_loc: bool | Location = Location.A4_TOWN_START
        self._runs = runs

    # BUY POTS & STASH WHEN AT PENTAGRAM
    def _cs_town_visit(self, location:str) -> bool:
        common.close() # close all windows and minimaps to see the TP
        belt.update_pot_needs()

        buy_pots = (
                    consumables.should_buy("health", min_needed = 2) or
                    consumables.should_buy("mana", min_needed = 2)
                )

        if not buy_pots:
            Logger.debug(location + ": Got enough pots, no need to go to town right now.")

        else:
            Logger.info(location + ": Going back to town to visit our friend Jamella (heal/clear debuffs/restock potions)")
            Logger.debug(f"Needs: {consumables.get_needs()}")
            success = self._char.tp_town()
            toggle_automap(True) # required to check if we are back in town
            if success:
                self._curr_loc = self._town_manager.wait_for_tp(self._curr_loc)
                set_pause_state(True) #pausing health monitor
                
                # Dismiss skill/quest/help/stats icon if they are on screen
                if not view.dismiss_skills_icon():
                    view.return_to_play()
                
                belt.update_pot_needs() # Look at belt to figure out how many pots need to be picked up
                items = None # Inspect inventory
            
                img = personal.open()
                # Update TP, ID, key needs
                
                self._use_id_tome = common.tome_state(img, 'id')[0] is not None
                self._use_keys = is_visible(ScreenObjects.Key, img)
            
                personal.update_tome_key_needs(img, item_type = 'tp')
                if self._use_id_tome:
                    personal.update_tome_key_needs(img, item_type = 'id')
                if self._use_keys:
                    # if keys run out then refilling will be unreliable :(
                    self._use_keys = personal.update_tome_key_needs(img, item_type = 'key')
            
                # Check inventory items
                if personal.inventory_has_items(img):
                    Logger.debug("Inspecting inventory items")
                    items = personal.inspect_items(img, game_stats=self._game_stats, close_window=False)
                common.close()

                toggle_automap(True) #might have been closed when dismissing quests etc.
                Logger.debug(f"Needs: {consumables.get_needs()}")
                if items:
                    # if there are still items that need identifying, go to cain to identify them
                    if any([item.need_id for item in items]):
                        Logger.info("ID items at cain")
                        self._curr_loc = self._town_manager.identify(self._curr_loc)
                        if not self._curr_loc:
                            Logger.warning("Issue with:" + str(self._curr_loc) + " ... aborting run")
                            return False
                        # recheck inventory
                        items = personal.inspect_items(game_stats=self._game_stats)
                keep_items = any([item.keep for item in items]) if items else None
                sell_items = any([item.sell for item in items]) if items else None
                stash_gold = personal.get_inventory_gold_full()

                # Check if should need some healing
                img = grab()
                need_refill = (
                    consumables.should_buy("health", min_needed = 3) or
                    consumables.should_buy("mana", min_needed = 3) or
                    (self._use_keys and consumables.should_buy("key", min_remaining = 4)) or
                    consumables.should_buy("tp", min_remaining = 3) or
                    consumables.should_buy("id", min_remaining = 3)
                )
                if need_refill or sell_items:
                    Logger.info("Buy consumables and/or sell items")
                    self._curr_loc, result_items = self._town_manager.buy_consumables(self._curr_loc, items = items)
                    if self._curr_loc:
                        items = result_items
                        sell_items = any([item.sell for item in items]) if items else None
                        Logger.debug(f"Needs: {consumables.get_needs()}")
                elif meters.get_health(img) < 0.6 or meters.get_mana(img) < 0.2:
                    Logger.info("Healing at next possible Vendor")
                    self._curr_loc = self._town_manager.heal(self._curr_loc)
                if not self._curr_loc:
                    Logger.warning("Issue with:" + str(self._curr_loc) + " ... aborting run")
                    return False

                # Stash stuff
                if keep_items or stash_gold:
                    Logger.info("Stashing items")
                    self._curr_loc, result_items = self._town_manager.stash(self._curr_loc, items=items)
                    sell_items = any([item.sell for item in result_items]) if result_items else None
                    #Logger.info("Running transmutes")
                    #self._transmute.run_transmutes(force=False)
                    common.close()
                    toggle_automap(True) #might have been closed when dismissing quests etc.
                    if not self._curr_loc:
                        Logger.warning("Issue with:" + str(self._curr_loc) + " ... aborting run")
                        return False
                    self._picked_up_items = False

                # Check if we are out of tps or need repairing
                need_repair = is_visible(ScreenObjects.NeedRepair)
                need_routine_repair = False if not Config().char["runs_per_repair"] else self._game_stats._run_counter % Config().char["runs_per_repair"] == 0
                need_refill_teleport = self._char.capabilities.can_teleport_with_charges and (not self._char.select_tp() or self._char.is_low_on_teleport_charges())
                if need_repair or need_routine_repair or need_refill_teleport or sell_items:
                    if need_repair:
                        Logger.info("Repair needed. Gear is about to break")
                    elif need_routine_repair:
                        Logger.info(f"Routine repair. Run count={self._game_stats._run_counter}, runs_per_repair={Config().char['runs_per_repair']}")
                    elif need_refill_teleport:
                        Logger.info("Teleport charges ran out. Need to repair")
                    elif sell_items:
                        Logger.info("Selling items at repair vendor")
                    self._curr_loc, result_items = self._town_manager.repair(self._curr_loc, items)
                    if self._curr_loc:
                        items = result_items
                    if not self._curr_loc:
                        Logger.warning("Issue with:" + str(self._curr_loc) + " ... aborting run")
                        return False

                # Check if merc needs to be revived
                if not is_visible(ScreenObjects.MercIcon) and Config().char["use_merc"]:
                    Logger.info("Resurrect merc")
                    self._game_stats.log_merc_death()
                    self._curr_loc = self._town_manager.resurrect(self._curr_loc)
                    if not self._curr_loc:
                        Logger.warning("Issue with:" + str(self._curr_loc) + " ... aborting run")
                        return False


                # Move from Act 4 NPC Jamella towards WP where we can see the Blue Portal
                if not self._pather.traverse_nodes_automap([164, 163], self._char, timeout=2): return False
                wait(0.22, 0.28)
                if (template_match := detect_screen_object(ScreenObjects.TownPortalReduced)).valid:
                    pos = template_match.center_monitor
                    pos = (pos[0], pos[1] + 30)
                    Logger.debug(location + ": Going through portal...")
                    # Note: Template is top of portal, thus move the y-position a bit to the bottom
                    mouse.move(*pos, randomize=6, delay_factor=[0.9, 1.1])
                    wait(0.08, 0.15)
                    mouse.click(button="left")
                    if loading.wait_for_loading_screen(2.0):
                        Logger.debug(location + ": Waiting for loading screen...")
                    set_pause_state(False) # activating health manager and inventory open check
                    # Recalibrate at Pentagram and set up new TP to improve loop back to penta success
                    common.close() # kets reset all maps & windows
                    toggle_automap(True)
                    if not self._pather.traverse_nodes_automap([1610], self._char, threshold=0.80, toggle_map=True): return False # we could also remove this calibration here, and put it in the if-block of the main block where the function is called.  this could allow us to do cs_townvisits anywhere.
                    if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                    Logger.info("Calibrated at Pentagram after visiting town")
        return True

    def spawncheck(self, timeout):
        timer = time.time()
        elapsed_time = time.time()
        counter = 0
        diablo_spawned = True
        Logger.debug("DIA: Waiting for Diablo Chat message")
        while not template_finder.search_and_wait(["DIA_AM_CHAT"], threshold=0.85, timeout=0.2, suppress_debug=True).valid:
            #Logger.debug("DIA: Waiting for Diablo Chat message, counter: " + str(counter) + ", time: " + str(round(elapsed_time)))
            elapsed_time = (time.time() - timer)
            counter += 1
            if elapsed_time > timeout:
                Logger.debug("DIA: Chat message did not appear after " + str(timeout) + " seconds")
                diablo_spawned = False
                break
        if diablo_spawned:
            Logger.debug("DIA: Chat message appeared after " + str(round(elapsed_time)) + "s - Diablo will spawn in 5 s, lets quickly go back to PENT")
            Logger.info("DIA: No need to check spawn indicator: Chat message was already positive"  + '\033[92m' + " :)" + '\033[0m')
            spawn_timer = time.time()
            diablo_spawned = True #hm, could it be that this is overriding the FALSE that is set in case the chat message does not appear?
        else:
            Logger.info("DIA: something seems wrong, Let's still continue to Diablo to check for a spawn template, maybe we are lucky")
            spawn_timer = time.time()
            diablo_spawned = False
        return spawn_timer, diablo_spawned

    def approach(self, start_loc: Location) -> bool | Location:
        Logger.info("Run Diablo")
        if not (self._char.capabilities.can_teleport_natively or self._char.capabilities.can_teleport_with_charges):
            raise ValueError("Diablo requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        waypoint.use_wp("River of Flame")
        return Location.A4_DIABLO_WP

    def open_fake_seal(self, seal_layout, node_seal1_automap, seal1_opentemplates: list) -> bool:
        toggle_automap(True)
        Logger.info(seal_layout +": Starting to pop seals")
        if not self._pather.traverse_nodes_automap(node_seal1_automap, self._char, toggle_map=False): return False # Calibrate at Fake seal
        for i in range(3):
            seal_pos = self._pather.find_abs_node_pos(node_seal1_automap[-1], grab(force_new=True), threshold=0.8, grayscale=False)
            x_m = random.randint(-10, 10)
            y_m = random.randint(-10, 10)
            if seal_pos is not None:
                x_m += seal_pos[0] * 8
                y_m += seal_pos[1] * 8 - 5
            toggle_automap(False)
            mouse.move(*convert_abs_to_monitor((x_m, y_m)))
            mouse.press(button="left")
            Logger.info(seal_layout +": Opening Fake Seal")
            time.sleep(0.2)
            mouse.release(button="left")
            result = template_finder.search_and_wait(seal1_opentemplates, self.seal_roi, timeout=1.0, threshold=0.7, suppress_debug=True)
            toggle_automap(True)
            if result.valid: break
            if i < 2:
                Logger.info(seal_layout +": Seal not open. Try again...")
        return True
    
    def open_real_seal(self, seal_layout: str, node_seal2_automap, seal2_opentemplates: list) -> bool:
        if not self._pather.traverse_nodes_automap(node_seal2_automap, self._char, toggle_map=False): return False # Calibrate at Boss seal
        for i in range(3):
            seal_pos = self._pather.find_abs_node_pos(node_seal2_automap[-1], grab(force_new=True), threshold=0.8, grayscale=False)
            if seal_pos is not None:
                x_m = seal_pos[0] * 8
                y_m = seal_pos[1] * 8 - 5
            else:
                x_m = 0
                y_m = 0
            toggle_automap(False)
            mouse.move(*convert_abs_to_monitor((x_m, y_m)))
            mouse.press(button="left")
            Logger.info(seal_layout +": Opening Boss Seal")
            time.sleep(0.2)
            mouse.release(button="left")
            if template_finder.search_and_wait(seal2_opentemplates, self.seal_roi, timeout=1.0, threshold=0.7, suppress_debug=True).valid:
                break
            if i < 2:
                toggle_automap(True)
                Logger.info(seal_layout +": Seal not open. Try again...")
        return True

    def battle(self, do_pre_buff: bool) -> bool | tuple[Location, bool]:
        diablo_spawned = False
        self._picked_up_items = False
        self.used_tps = 0
        if do_pre_buff: self._char.pre_buff()

        xp, yp = self._pather._nodes[1620]['DIA_AM_PENT']
        xc, yc = self._pather._nodes[1620]['DIA_AM_CR1_2']
        cr1_pent_x = xp - xc
        cr1_pent_y = yp - yc

        #CS TOWNVISITS TEST
        #if Config().char["dia_town_visits"]: 
        #    Logger.debug("drink pots!")
        #    toggle_automap(False)
        #    self._cs_town_visit("A")

        ##############
        # WP to PENT #
        ##############
        
        #Teleport directly
        if self._char.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("dia_wp_cs-e", self._char) #Traverse River of Flame (no chance to traverse w/o fixed, there is no reference point between WP & CS Entrance) - minimum 3 teleports are needed, if we only cross the gaps (maybe loop template matching the gap, otherwise walking), otherwise its 9

        #Traverse ROF with minimal teleport charges
        elif not self._char.run_to_cs() and self._char.capabilities.can_teleport_with_charges:
            Logger.debug("ROF: Let's run to the ROF diving board!")

            pos_m = convert_abs_to_monitor((620, -350))
            self._char.walk(pos_m, force_move=True) # walk away from wp
            # go to the first jumping spot at ROF
            if not self._pather.traverse_nodes_automap([1601, 1602], self._char, timeout=2, force_move=True): return False
            path_to_cs_entrance = [convert_abs_to_screen((620, -350))] * 7 #maybe bring down to 6?
            self._pather.traverse_nodes_fixed(path_to_cs_entrance, self._char)

            Logger.debug("ROF: found CS Entrance!")
            #self._pather.traverse_nodes_fixed("dia_tyrael_cs-e", self._char) #never teleports, always walks...

        else: 
            raise ValueError("Diablo requires teleport")

        #So we finally arrived at CS Entrance
        if not self._pather.traverse_nodes_automap([1605], self._char): return False # Calibrate at CS Entrance
        Logger.debug("ROF: Calibrated at CS ENTRANCE")
        
        #make leecher TP
        if Config().char["dia_leecher_tp_cs"]:
            Logger.debug("CS: OPEN LEECHER TP AT ENTRANCE")
            self._char.dia_kill_trash("aisle_2") #clear the area aound TP #DIA_CLEAR_TRASH=1 , DIA_CS_LEECHER_TP=1
            if not skills.has_tps(): Logger.warning("CS: failed to open TP, you should buy new TPs!")
            mouse.click(button="right")
                
        #############################
        # KILL TRASH IN CS ENTRANCE #
        #############################

        if Config().char["dia_kill_trash"]:

            if Config().char["safer_routines"]: #go back to clear mobs up to entrance to avoid leechers getting smacked by stray mobs in hardcore
                Logger.debug("ROF: Clearing around the TP to make it more safe for leechers (safer_routines=1)")
                trash_leecher = [(1500,"outside_cs"), (1501,"outside_cs_stairs"), (1502,"aisle_1"), (1503,"aisle_2"), (1504,"aisle_3")]
                for node, name in trash_leecher:
                    if not self._pather.traverse_nodes_automap([node], self._char): return False
                    Logger.debug(f"CS TRASH: Killing Trash at: {name}")
                    self._char.dia_kill_trash(name)

            trash_cs_en = [(1505,"aisle_4"), (1506,"hall1_1"), (1507,"hall1_2")]
            if Config().char["safer_routines"]:
                trash_cs_en += [(1508,"hall1_3"), (1509,"hall1_4"), (1510,"to_hall2_1")]
            trash_cs_en += [(1511,"to_hall2_2"),(1513,"to_hall2_4"),(1514,"hall2_1")]
            if Config().char["safer_routines"]:
                trash_cs_en += [(1515,"hall2_2"),(1516,"hall2_3"),(1517,"hall2_4")]
            for node, name in trash_cs_en:
                if not self._pather.traverse_nodes_automap([node], self._char): return False
                Logger.debug(f"CS TRASH: Killing Trash at: {name}")
                self._char.dia_kill_trash(name)

            if not self._pather.traverse_nodes_automap([1516,1514,1518], self._char): return False #pickit inv check
            Logger.debug("CS TRASH: Killing Trash at: to_hall3_1")
            self._char.dia_kill_trash("to_hall3_1")

            trash_cs_en = [(1520,"to_hall3_3")]
            if Config().char["safer_routines"]:
                trash_cs_en += [(1522,"hall3_2"), (1523,"hall3_3"), (1524,"hall3_4"), (1525,"hall3_5")]

            for node, name in trash_cs_en:
                if not self._pather.traverse_nodes_automap([node], self._char): return False
                Logger.debug(f"CS TRASH: Killing Trash at: {name}")
                self._char.dia_kill_trash(name)

        else:
            #we kill no trash
            Logger.debug("ROF: Teleporting directly to PENTAGRAM")
            to_cr1 = [(1160,10)] * 7
            self._pather.traverse_nodes_fixed(to_cr1, self._char)

        if Config().char["dia_leecher_tp_pent"]:
            if not self._pather.traverse_nodes_automap([1522], self._char): return False # go a bit into hall3, so that the TP does not obscure our pentagram template with a yellow automap marker.
            Logger.debug("CS: OPEN LEECHER TP AT ENTRANCE")
            self._char.dia_kill_trash("pent_before_a")
            if not skills.has_tps(): Logger.warning("CS: failed to open TP, you should buy new TPs!")
            mouse.click(button="right")

        self.seal_roi = [*convert_abs_to_screen((-200,-220)), 400, 400]
        ##########
        # Seal A #
        ##########

        # Settings
        sealname = "A"
        boss = "Vizier"
        seal_layout1= "A1-L"
        seal_layout2= "A2-Y"

        ###############
        # PREPARATION #
        ###############
        
        
        if Config().char["dia_town_visits"]: 
            toggle_automap(False)
            self._cs_town_visit("A")

        #############################
        # KILL TRASH TOWARDS SEAL A #
        #############################

        if Config().char["dia_kill_trash"]:
            if do_pre_buff:
                self._char.pre_buff() #only for dia_kill_trash
            self._char.dia_kill_trash("pent_before_a") # Clear Pentagram
            Logger.debug("CS TRASH: Kill Trash between Pentagram and Layoutcheck A")
            trash_a = [(1525, "hall3_5"), (1526, "trash_to_a1"), (1529, "trash_to_a4"), (1627, "a_boss")]
            if Config().char["safer_routines"]:
                trash_a.insert(2, (1527, "trash_to_a2"))
                trash_a.insert(3, (1528, "trash_to_a3"))
            for node, name in trash_a:
                if not self._pather.traverse_nodes_automap([node], self._char): return False
                Logger.debug(f"CS TRASH: Killing Trash at: {name}")
                self._char.dia_kill_trash(name)
       
        ###############
        # LAYOUTCHECK #
        ###############

        to_seal_a = [(120,10), (80,10), (80,10)]
        self._pather.traverse_nodes_fixed(to_seal_a, self._char)
        if not self._pather.traverse_nodes_automap([1620], self._char, threshold=0.85, toggle_map=True): return False
        self._char.dia_kill_trash("layoutcheck_a") # Clear Trash & Loot at Layout Check

        toggle_automap(True)
        Logger.debug("==============================")
        Logger.debug(f"Checking Layout for "f"{boss}") #{sealname}: 
        wait(0.25, 0.35)
        img = grab()
        #any of three templates, the animations of the flames disturb the image. other option would be to match 3x with higher threshold in small intervals
        cr1 = template_finder.search(["DIA_AM_CR1_2", "DIA_AM_CR1_1", "DIA_AM_CR1"], img, threshold=0.8)
        layout = 0
        if cr1.valid:
            x, y = cr1.center
            lc_roi = [x-190, y-130, 160, 80]
            lc_match = template_finder.search("DIA_AM_CITADEL", img, threshold=0.8, roi=lc_roi) #we should print the threshold to debug log - lowered from 0.9 to 0.8
            if lc_match.valid:
                dx = lc_match.center[0] - x
                dy = lc_match.center[1] - y
                Logger.info(f"{sealname}: Find citadel offset at ({dx}, {dy})")
                layout = 1 if dx > -100 else 2
            else:
                Logger.warning(f"{sealname}: Failed to find citadel")
                cv2.imwrite(f"./log/screenshots/info/{sealname}_citadel_fail_{time.strftime('%Y%m%d_%H%M%S')}.png", cut_roi(img, lc_roi))
        if layout == 0:
            Logger.warning(f"{sealname}: Layout_check failure - could not determine the seal Layout at "f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + sealname + "_LC_fail" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            wait(5)
            return False

        if layout == 1:
            Logger.info(f"{seal_layout1}: Templates found")
            
            ###################
            # Clear Seal A1-L #
            ###################

            #CLEAR TRASH
            if Config().char["dia_kill_trash"]:
                toggle_automap(False)
                Logger.info(seal_layout1 +": Starting to clear seal")
                Logger.debug("Kill Trash at SEAL A not implemented yet")
                for i in [1,2,3]:
                    Logger.debug(f"{seal_layout1}_0{i}: Kill trash")
                    self._char.dia_kill_trash(f"{seal_layout1}_0{i}")
        
            #SEAL
            if not self.open_fake_seal(seal_layout1, [1621], ["DIA_A1L2_14_OPEN"]): return False
            if not self.open_real_seal(seal_layout1, [1622], ["DIA_A1L2_5_OPEN"]): return False

            Logger.debug(seal_layout1 + ": Kill Boss A (Vizier)") 
            self._char.kill_vizier_automap(seal_layout1) # Kill Boss
            Logger.debug(seal_layout1 + ": Traversing back to Pentagram")
            if not self._pather.traverse_nodes_automap([1610], self._char): return False # go to Pentagram
            if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
            Logger.info(seal_layout1 + ": finished seal & calibrated at PENTAGRAM")
        
        else:
            Logger.debug(f"{seal_layout2}: Templates found")

            ###################
            # Clear Seal A2-Y #
            ###################

            #CLEAR TRASH
            if Config().char["dia_kill_trash"]:
                toggle_automap(False)
                Logger.info(seal_layout2 +": Starting to clear seal")
                Logger.debug("Kill Trash at SEAL A not implemented yet")
                for i in [1,2,3]:
                    Logger.debug(f"{seal_layout2}_0{i}: Kill trash")
                    self._char.dia_kill_trash(f"{seal_layout2}_0{i}")

            #SEAL
            if not self.open_fake_seal(seal_layout2, [1624], ["DIA_A2Y4_29_OPEN"]): return False

            if self._char.capabilities.can_teleport_with_charges:
                if not self._pather.traverse_nodes_automap([1627], self._char, toggle_map=False): return False # take a sidestep to not get stuck
            if not self.open_real_seal(seal_layout2, [1625], ["DIA_A2Y4_36_OPEN"]): return False

            Logger.debug(seal_layout2 + ": Kill Boss A (Vizier)")
            self._char.kill_vizier_automap(seal_layout2)
            Logger.debug(seal_layout2 + ": Traversing back to Pentagram")
            if self._char.capabilities.can_teleport_with_charges:
                if not self._pather.traverse_nodes_automap([1627], self._char): return False # take a sidestep to not get stuck
            if not self._pather.traverse_nodes_automap([1610], self._char): return False
            if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
            Logger.info(seal_layout2 + ": finished seal & calibrated at PENTAGRAM")
        

        ##########
        # Seal B #
        ##########

        # Settings
        sealname = "B"
        boss = "De Seis"
        seal_layout1= "B2-U"
        seal_layout2= "B1-S"

        ###############
        # PREPARATION #
        ###############
        
        if Config().char["dia_town_visits"]: 
            toggle_automap(False)
            self._cs_town_visit("B")
        
        if do_pre_buff and Config().char["dia_kill_trash"] or Config().char["safer_routines"]: self._char.pre_buff()  #only for dia_kill_trash and safer routine
        self._char.dia_kill_trash("pent_before_b") # Clear Pentagram

        #############################
        # KILL TRASH TOWARDS SEAL B #   ## has to be reworked for walking chars. requires too many charges
        #############################

        if Config().char["dia_kill_trash"]:
            Logger.debug("CS TRASH: Kill Trash between Pentagram and Layoutcheck B")

            trash_b = [
                (1530, "hall3_5", False), (1531, "trash_to_b1", False), (1532, "trash_to_b2", False), (1633, "approach_b1s", False),
                (1638, "approach_b2u", True), (1632, "a_boss", False), (1635, "b_boss_seal", True)
            ]
            for node, name, tp_charge in trash_b:
                if not self._pather.traverse_nodes_automap([node], self._char, use_tp_charge=tp_charge): return False
                Logger.debug(f"CS TRASH: Killing Trash at: {name}")
                self._char.dia_kill_trash(name)

        ###############
        # LAYOUTCHECK #
        ###############

        if not self._pather.traverse_nodes_automap([1630], self._char, threshold=0.78, toggle_map=True): return False
        self._char.dia_kill_trash("layoutcheck_b")
        Logger.debug("==============================")
        Logger.debug(f"Checking Layout for "f"{boss}") #{sealname}: 
        
        toggle_automap(True)
        wait(0.25, 0.35)
        img = grab()
        cr1 = template_finder.search(["DIA_AM_CR1_2", "DIA_AM_PENT"], img, threshold=0.8)
        layout = 0
        if cr1.valid:
            x, y = cr1.center
            if cr1.name == "DIA_AM_PENT":
                # convert reference from pent to cr1
                x += cr1_pent_x
                y += cr1_pent_y
            lc_roi = [x+250, y-180, 250, 100]
            lc_match = template_finder.search("DIA_AM_CITADEL", img, threshold=0.7, roi=lc_roi) #lowered from .85
            if lc_match.valid:
                dx = lc_match.center[0] - x
                dy = lc_match.center[1] - y
                Logger.info(f"{sealname}: Find citadel offset at ({dx}, {dy})")
                layout = 2 if dy < -150 else 1
            else:
                Logger.warning(f"{sealname}: Failed to find citadel")
                cv2.imwrite(f"./log/screenshots/info/{sealname}_citadel_fail_{time.strftime('%Y%m%d_%H%M%S')}.png", cut_roi(img, lc_roi))
        else:
             Logger.warning(f"{sealname}: Failed to find DIA_AM_CR1, _1 or _2")
             cv2.imwrite(f"./log/screenshots/info/{sealname}_cr1_fail_{time.strftime('%Y%m%d_%H%M%S')}.png", img)

        if layout == 0:
            Logger.warning(f"{sealname}: Layout_check failure - could not determine the seal Layout at "f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + sealname + "_LC_fail" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            wait(5)
            return False

        if layout == 1:
            Logger.info(f"{seal_layout1}: Templates found")
            
            ###################
            # Clear Seal B2-U #
            ###################

            #CLEAR TRASH
            if Config().char["dia_kill_trash"]:
                toggle_automap(False)
                Logger.info(seal_layout1 +": Starting to clear seal")
                Logger.debug("Kill Trash at SEAL B not implemented yet")
                for i in [1,2,3]:
                    Logger.debug(f"{seal_layout1}_0{i}: Kill trash")
                    self._char.dia_kill_trash(f"{seal_layout1}_0{i}")
               
            #SEAL
            toggle_automap(True)
            Logger.info(seal_layout1 +": Starting to pop seals")
            if not self.open_real_seal(seal_layout1, [1635], ["DIA_B2U2_16_OPEN"]): return False

            Logger.debug(seal_layout1 + ": Kill Boss B (DeSeis)")
            self._char.kill_deseis_automap(seal_layout1)
            Logger.debug(seal_layout1 + ": Traversing back to Pentagram")
            if not self._pather.traverse_nodes_automap([1610], self._char): return False
            if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
            Logger.info(seal_layout1 + ": finished seal & calibrated at PENTAGRAM")   
    
            #Trash B Back to Pent = [1635, 1632, 1638, 1633, 1533, 1610]
        else:
            Logger.info(f"{seal_layout2}: Templates found")
            ###################
            # Clear Seal B1-S #
            ###################

            #CLEAR TRASH
            if Config().char["dia_kill_trash"]:
                toggle_automap(False)
                Logger.info(seal_layout2 +": Starting to clear seal")
                Logger.debug("Kill Trash at SEAL B not implemented yet")
                for i in [1,2,3]:
                    Logger.debug(f"{seal_layout2}_0{i}: Kill trash")
                    self._char.dia_kill_trash(f"{seal_layout2}_0{i}")

            #SEAL
            toggle_automap(True)
            Logger.info(seal_layout2 +": Starting to pop seals")
            if not self.open_real_seal(seal_layout2, [1631], ["DIA_B1S2_23_OPEN"]): return False

            Logger.debug(seal_layout2 + ": Kill Boss B (DeSeis)")
            self._char.kill_deseis_automap(seal_layout2)
            Logger.debug(seal_layout2 + ": Traversing back to Pentagram")
            if not self._pather.traverse_nodes_automap([1610], self._char): return False
            if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
            Logger.info(seal_layout2 + ": finished seal & calibrated at PENTAGRAM")
            #Trash B Back to Pent = [1635, 1632, 1638, 1633, 1533, 1610]
        
        ##########
        # Seal C #
        ##########

        # Settings
        sealname = "C"
        boss = "Infector"
        seal_layout1= "C1-F"
        seal_layout2= "C2-G"

        ###############
        # PREPARATION #
        ###############
        
        if Config().char["dia_town_visits"]: 
            toggle_automap(False)
            self._cs_town_visit("C")
        if do_pre_buff and Config().char["dia_kill_trash"] or Config().char["safer_routines"]: self._char.pre_buff() #only for dia_kill_trash and safer routine
        self._char.dia_kill_trash("pent_before_c") # Clear Pentagram

        #############################
        # KILL TRASH TOWARDS SEAL C #
        #############################

        if Config().char["dia_kill_trash"]:
            Logger.debug("CS TRASH: Kill Trash between Pentagram and Layoutcheck C")

            trash_c = [(1534,"trash_to_c1"), (1535,"trash_to_c2"), (1536,"trash_to_c3"), (1644,"approach_c2g"), (1645,"fake_c2g")]
            for node, name in trash_c:
                if not self._pather.traverse_nodes_automap([node], self._char): return False
                Logger.debug(f"CS TRASH: Killing Trash at: {name}")
                self._char.dia_kill_trash(name)

        ###############
        # LAYOUTCHECK #
        ###############

        if not self._pather.traverse_nodes_automap([1640], self._char, threshold=0.83, toggle_map=True): return False
        self._char.dia_kill_trash("layoutcheck_c") # Clear Trash & Loot at Layout Check
        Logger.debug("==============================")
        Logger.debug(f"Checking Layout for "f"{boss}") #{sealname}: 
        
        toggle_automap(True)
        wait(0.25, 0.35)
        img = grab()
        cr1 = template_finder.search(["DIA_AM_CR1_2", "DIA_AM_PENT"], img, threshold=0.8)
        layout = 0
        if cr1.valid:
            x, y = cr1.center
            if cr1.name == "DIA_AM_PENT":
                # convert reference from pent to cr1
                x += cr1_pent_x
                y += cr1_pent_y
            lc_roi = [x+390, y+90, 100, 100]
            lc_match = template_finder.search("DIA_AM_CITADEL", img, threshold=0.8, roi=lc_roi) #lowered from 0.9
            if lc_match.valid:
                dx = lc_match.center[0] - x
                dy = lc_match.center[1] - y
                Logger.info(f"{sealname}: Find citadel offset at ({dx}, {dy})")
                layout = 1 if (dx < 420 and dy > 140) or (dx > 440 and dy < 130) else 2
            else:
                Logger.warning(f"{sealname}: Failed to find citadel")
                cv2.imwrite(f"./log/screenshots/info/{sealname}_citadel_fail_{time.strftime('%Y%m%d_%H%M%S')}.png", cut_roi(img, lc_roi))

        if layout == 0:
            Logger.warning(f"{sealname}: Layout_check failure - could not determine the seal Layout at "f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + sealname + "_LC_fail" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            wait(5)
            return False

        if layout == 1:
            Logger.info(f"{seal_layout1}: Templates found")
            
            ###################
            # Clear Seal C1-F #
            ###################

            #CLEAR TRASH
            if Config().char["dia_kill_trash"]:
                toggle_automap(False)
                Logger.info(seal_layout1 +": Starting to clear seal")
                Logger.debug("Kill Trash at SEAL C not implemented yet")
                for i in [1,2,3]:
                    Logger.debug(f"{seal_layout1}_0{i}: Kill trash")
                    self._char.dia_kill_trash(f"{seal_layout1}_0{i}")
           
            #SEAL
            if not self.open_fake_seal(seal_layout1, [1641], ["dia_am_c1f_fake_open"]): return False
            if not self.open_real_seal(seal_layout1, [1642], ["dia_am_c1f_open"]): return False
            
            Logger.debug(seal_layout1 + ": Kill Boss C (Infector)")
            self._char.kill_infector_automap(seal_layout1)

            ######################
            # DIABLO SPAWN CHECK #
            Logger.info("Waiting for Diablo to spawn") # we check when still being at seal C, because pickit sometimes takes longer, so the message appears whilst traversing, putting us at risk to miss it
            spawn_timer, diablo_spawned = self.spawncheck(10)
            ######################

            Logger.debug(seal_layout1 + ": Traversing back to Pentagram")
            if not self._pather.traverse_nodes_automap([1610], self._char): return False
            if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
            Logger.info(seal_layout1 + ": finished seal & calibrated at PENTAGRAM")     
            #Trash C back to Pent = [1645, 1648, 1536, 1537]
        else:
            Logger.info(f"{seal_layout2}: Templates found")
            ###################
            # Clear Seal C2-G #
            ###################

            #CLEAR TRASH
            if Config().char["dia_kill_trash"]:
                toggle_automap(False)
                Logger.info(seal_layout2 +": Starting to clear seal")
                Logger.debug("Kill Trash at SEAL C not implemented yet")
                for i in [1,2,3]:
                    Logger.debug(f"{seal_layout2}_0{i}: Kill trash")
                    self._char.dia_kill_trash(f"{seal_layout2}_0{i}")

            #SEAL
            if not self.open_fake_seal(seal_layout2, [1645], ["DIA_C2G2_7_OPEN"]): return False
            if not self.open_real_seal(seal_layout2, [1646], ["DIA_C2G2_21_OPEN"]): return False

            Logger.debug(seal_layout2 + ": Kill Boss C (Infector)")
            self._char.kill_infector_automap(seal_layout2)

            ######################
            # DIABLO SPAWN CHECK #
            Logger.info("Waiting for Diablo to spawn") # we check when still being at seal C, because pickit sometimes takes longer, so the message appears whilst traversing, putting us at risk to miss it
            spawn_timer, diablo_spawned = self.spawncheck(10)
            ######################

            Logger.debug(seal_layout2 + ": Traversing back to Pentagram") #hoping that takes less than 5s
            if self._char.capabilities.can_teleport_with_charges:
                if not self._pather.traverse_nodes_automap([1645], self._char): return False # take a sidestep to not get stuck
            if not self._pather.traverse_nodes_automap([1610], self._char): return False
            if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
            Logger.info(seal_layout2 + ": finished seal & calibrated at PENTAGRAM")
            #Trash C back to Pent = [1645, 1648, 1536, 1537]
        
        ##########
        # Diablo #
        ##########
        
        if not self._pather.traverse_nodes_automap([1610], self._char): return False
        if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())     

        if not diablo_spawned: # message check failed, so let's check again at the pentagram - could be that in case a blastwave is coming, the template is matched
            diablo_spawned = template_finder.search_and_wait(["DIA_AM_SPAWN", "DIA_AM_CHAT"], threshold=0.85, timeout=0.2)
            Logger.info("DIA spawn indicator: positive"  + '\033[92m' + " :)" + '\033[0m')
            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_dia_spawnindicator_positive" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
            diablo_spawned = True
        
        """
        else: # suprisingly returned a failed run, even though Diablo was spawned, maybe threshold should be increased?
            if template_finder.search_and_wait(["DIA_AM_NOSPAWN"], threshold=0.85, timeout=0.2).valid:
                Logger.info("DIA: spawn indicator: confirmed to be negative - aborting run" + '\033[91m' + " :(" + '\033[0m')
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_dia_spawnindicator_negative" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                return False
            else:        
                Logger.info("DIA: spawn indicator: not found - trying to kill anways"  + '\033[43m' + " ???" + '\033[0m') #if there is a blastwave, the template is masked
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_dia_spawnindicator_notfound" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                diablo_spawned = True
        """

        #COUNT ITEMS BEFORE KILL
        Logger.info("DIA: Taking Loot Screenshot before killing Diablo")
        keyboard.send(Config().char["show_items"]) #on
        loot_before = grab(force_new=True)
        keyboard.send(Config().char["show_items"]) #off
        item_count_before = len(d2r_image.get_ground_loot(loot_before).items.copy())
        Logger.info("DIA: FYI item count before kill: "+str(item_count_before))

        """
        #DEBUG
        #now = time.time()
        #Logger.debug("spawn: " +str(spawn_timer))
        #Logger.debug("now: " +str(now))
        #wait(1)
        #now = time.time()
        #Logger.debug("now +1s: " +str(now))
        #Logger.debug("now +1s: " +str(spawn_timer - now))
        
        #while spawn_timer - now < 5:
        #  Logger.info("DIA: Waiting at Pentagram for Diablo to spawn")  # not needed, the time we need to go to pent from seal-C after the spawn message arrived is perfect to have him there
        """

        Logger.info("DIA: Killing Diablo")
        self._char.kill_diablo()

        #COUNT ITEMS AFTER KILL
        Logger.info("DIA: Taking Loot Screenshot after killing Diablo")
        keyboard.send(Config().char["show_items"]) #on
        loot_after = grab(force_new=True)
        keyboard.send(Config().char["show_items"]) #off
        item_count_after = len(d2r_image.get_ground_loot(loot_after).items.copy())
        Logger.debug("DIA: FYI item count after kill: "+str(item_count_after)+ ", Item count diff: " + str(item_count_before - item_count_after))

        if item_count_before == item_count_after:
            Logger.warning("DIA: Seems like we did not kill Diablo yet, we repeat the attack sequence one more time")
            self._char.kill_diablo()

            Logger.info("DIA: Taking Loot Screenshot after killing Diablo")
            keyboard.send(Config().char["show_items"]) #on
            loot_after = grab(force_new=True)
            keyboard.send(Config().char["show_items"]) #off
            item_count_after = len(d2r_image.get_ground_loot(loot_after).items.copy())
            Logger.debug("DIA: FYI item count after kill: "+str(item_count_after))
            Logger.debug("DIA: Item count diff: " + str(item_count_after - item_count_before))

            if not item_count_before == item_count_after:
                Logger.info("DIA: There you go, we killed him!")
        else:
            Logger.info("DIA: There you go, we killed him!")

        Logger.info("DIA: Picking up Items")
        self._picked_up_items = self._pickit.pick_up_items(char=self._char) #commented for now, causes an error
        wait(0.5, 0.7)
        return (Location.A4_DIABLO_END, self._picked_up_items)

        #############
        # TODO LIST #
        #############
        
        # infector C1F is causing too many chicken right now -> we should consider hardcoding seals
        # B1S occasionally misses de seis if he spawns far upwards and walks to top (out of vision) - might need to add a second attack pattern here
        # B2U if de seis spawns at new spawn, we miss him.
        # automap shrine detection is broken -> switched templates didnt fix it
        # recalibrate after looting bosses, you get carried away in one direction whilst pickit, losing the second direction if there were mobs
        # implement safe_runs param for seal bosses to walk along the seal (and maybe clear it whilst doing so?)
        # implement river trasverse fixed using charges (or make a chain of "move" commands) - check if maybe we can loop that from WP until CS entrance template is found to avoid fixed path.
        # move mouse away during layout checks to avoid hovering an item that obscures the minimap (implemented, but still occasionally causes a missed seal)
        # consider a name-tag & name-lock for seal bosses & diablo
        # add walkadin pathing (Seal B is teleporting a lot right now)
        # revert back to classical template checks in case the initial check with minimap was bad (merc running around) - or just repeat it by recalibration at LC (hoping the merc goes somewhere else) - or mapcheck through map diff, isolate minimap by waiting a bit between checks, to isolate movement (E.g. merc)
        # check to have sufficient charges left before running CS (calculate how many are needed 7x for ROF + 2x for each sealboss)
        # has to be reworked for walking chars. requires too many charges
        # namelock dia
        # time the spawn of dia & start of attack sequence based on the chat message that is sent when he arrives, death could be monitored using the blue swirling animation occuring when he dies
