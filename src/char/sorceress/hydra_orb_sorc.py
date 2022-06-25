import time
import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait
import random
from pather import Pather, Location
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from config import Config
from target_detect import get_visible_targets
from item.pickit import PickIt

class HydraOrbSorc(Sorceress):
    def __init__(self, skill_hotkeys: dict, pather: Pather, pickit: PickIt):
        Logger.info("Setting up HydraOrbSorc Sorc")
        super().__init__(skill_hotkeys, pather)
        self._pickit = pickit
        self._pather = pather
        self._picked_up_items = False
        self._hydra_time = None
        self._frozen_orb_time = None

    def _skill(self, hotkey: str, count: int, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        for _ in range(count):
            if not self._skill_hotkeys[hotkey]:
                raise ValueError(f'You did not set a hotkey for {hotkey}!')
            keyboard.send(self._skill_hotkeys[hotkey])
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _fireball(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 10, count: int = 5):
        self._skill('fireball', count, cast_pos_abs, delay, spray)

    def _frozen_orb(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 0, count: int = 1, force_recast: bool = False):
        if force_recast or self._frozen_orb_time is None or time.time() - self._frozen_orb_time > 3:
            self._frozen_orb_time = time.time()
            self._skill('frozen_orb', count, cast_pos_abs, delay, spray)

    def _fb_orb(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), fireball_spray: float = 10, frozen_orb_spray: float = 0, count: int = 2):
        start = time.time()
        while time.time() - start < count:
            self._frozen_orb(cast_pos_abs, delay=delay, spray=frozen_orb_spray, count=1)
            self._fireball(cast_pos_abs, delay=delay, spray=fireball_spray, count=1)

    def _hydra(self, cast_pos_abs: tuple[float, float], spray: float = 10, count = 6, force_recast: bool = False):
        if force_recast or self._hydra_time is None or time.time() - self._hydra_time > 10:
            if not self._skill_hotkeys["hydra"]:
                raise ValueError("You did not set a hotkey for hydra!")
            keyboard.send(self._skill_hotkeys["hydra"])
            self._hydra_time = time.time()
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(count / 3, count / 2)
            mouse.release(button="right")

    def _attack(self, abs_pos: tuple[int, int], atk_len: float, hydra_spray: float = 0, hydra_count: int = 6, fireball_spray: float = 10, frozen_orb_spray: float = 0, force_recast: bool = False):
        for atk in range(int(atk_len)):
            self._hydra(abs_pos, spray=hydra_spray, force_recast=force_recast, count=hydra_count)
            self._fb_orb(abs_pos, fireball_spray=fireball_spray, frozen_orb_spray=frozen_orb_spray, count=2, delay=(self._cast_duration, self._cast_duration + 0.2))

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float, hydra_spray: float = 0, fireball_spray: float = 10):
        pos_m = convert_abs_to_monitor(abs_move)
        for atk in range(int(atk_len)):
            self._hydra(pos_m, spray=hydra_spray)
            self._fb_orb(pos_m, fireball_spray=fireball_spray)
        self.pre_move()
        self.move(pos_m, force_move=True)

    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.8, pindle_pos_abs[1] * 0.8]
        self._frozen_orb(cast_pos_abs)
        self._attack(cast_pos_abs, Config().char["atk_len_pindle"], fireball_spray=11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("pindle_end", self)
        self._hydra_time = None
        return True

    def kill_eldritch(self) -> bool:
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.8, eld_pos_abs[1] * 0.8]
        self._attack(cast_pos_abs, Config().char["atk_len_eldritch"], fireball_spray=75, frozen_orb_spray=100, hydra_spray=0)
        self._hydra(cast_pos_abs, count=3, force_recast=True)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("eldritch_end", self)
        self._hydra_time = None
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._pather.find_abs_node_pos(149, grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 1.1, shenk_pos_abs[1] * 1.1]
        self._frozen_orb(cast_pos_abs)
        self._attack(cast_pos_abs, Config().char["atk_len_shenk"] * 0.5, fireball_spray=90, frozen_orb_spray=200, hydra_count=6)
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_tp=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 1.01, shenk_pos_abs[1] * 1.01]
        self._attack(cast_pos_abs, Config().char["atk_len_shenk"] * 0.5, fireball_spray=90, frozen_orb_spray=200, force_recast=True)
        wait(self._cast_duration, self._cast_duration + 1)
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 1.01, shenk_pos_abs[1] * 1.01]
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        self._hydra_time = None
        return True

    ## Experimental
    def kill_summoner(self) -> bool:
        # move mouse to below altar
        # pos_m = convert_abs_to_monitor((0, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        cast_pos_abs = np.array([0, 0])
        # Move a bit back and another round
        self._attack(pos_m, int(Config().char["atk_len_arc"]), fireball_spray=15, force_recast=True, hydra_count=3)
        wait(0.1, 0.15)
        for atk in range(int(Config().char["atk_len_arc"])):
            self._hydra(pos_m, spray=0)
        return True

    ## Experimental
    def kill_deseis(self, seal_layout:str) -> bool:
        if seal_layout == "B1-S":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis", self) # quite aggressive path, but has high possibility of directly killing De Seis with first hammers, for 50% of his spawn locations
            nodes1 = [632]
            nodes2 = [631]
            nodes3 = [632]
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking De Seis at position 1/4")
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_deseis"] * 0.2)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_deseis"] * 0.2)

            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, timeout=3)
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_deseis"] * 0.2)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_deseis"] * 0.2)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_deseis"] * 0.2)
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, timeout=3)
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"] * 0.5)
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"] * 0.5)
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"] * 0.5)
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"] * 0.5)
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, timeout=3)
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"])  # no factor, so merc is not reset by teleport and he his some time to move & kill stray bosses
                wait(0.1, 0.2)
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"] * 0.5)
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"] * 0.5)
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"] * 0.5)

            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif seal_layout == "B2-U":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_b2u_644_646", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            #self._pather.traverse_nodes_fixed("dia_b2u_seal_deseis", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            nodes1 = [640]
            nodes2 = [646]
            nodes3 = [641]
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking De Seis at position 1/4")
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_deseis"] * 0.2)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_deseis"] * 0.2)
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_deseis"] * 0.2)
            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, timeout=3)
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_deseis"] * 0.2)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_deseis"] * 0.2)
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_deseis"] * 0.2)
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, timeout=3)
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"] * 0.5)
                self._move_and_attack((10, 10), Config().char["atk_len_diablo_deseis"] * 0.5)
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, timeout=3)
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                self._move_and_attack((0, 0), Config().char["atk_len_diablo_deseis"])  # no factor, so merc is not reset by teleport and he his some time to move & kill stray bosses
                wait(0.1, 0.2)
                self._move_and_attack((10, 10), Config().char["atk_len_diablo_deseis"] * 0.5)
                self._move_and_attack((10, 10), Config().char["atk_len_diablo_deseis"] * 0.5)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([641], self): return False # , timeout=3):
            if not self._pather.traverse_nodes([646], self): return False # , timeout=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([646], self): return False # , timeout=3):
            if not self._pather.traverse_nodes([640], self): return False # , timeout=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)

        else:
            Logger.warning(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
            return False
        return True

    ## Experimental
    def kill_vizier(self, seal_layout:str) -> bool:
        if seal_layout == "A1-L":
            ### APPROACH ###
            if not self._pather.traverse_nodes([612], self): return False # , timeout=3):
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_vizier"] * 0.5)
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([611], self, timeout=3)
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_vizier"]) # no factor, so merc is not reset by teleport and he his some time to move & kill stray bosses
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)
                wait(0.3, 1.2)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , timeout=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , timeout=3): # recalibrate after loot

        elif seal_layout == "A2-Y":
            ### APPROACH ###
            if not self._pather.traverse_nodes([627, 622], self): return False # , timeout=3):
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_vizier"] * 0.5)
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([623], self, timeout=3)
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_vizier"] * 0.5)
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)
            Logger.debug(seal_layout + ": Attacking Vizier at position 3/3")
            if not self._pather.traverse_nodes([624], self): return False
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)
                self._move_and_attack((-30, -15), Config().char["atk_len_diablo_vizier"])
                wait(0.1, 0.15)
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_vizier"] * 0.5)

            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([624], self): return False
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.debug(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([622], self): return False #, timeout=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([622], self): return False # , timeout=3): #recalibrate after loot

        else:
            Logger.warning(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
            return False
        return True

    def kill_infector(self, seal_layout:str) -> bool:
        if seal_layout == "C1-F":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_c1f_652", self)
            ### ATTACK ###
            pos_m = convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            Logger.debug(seal_layout + ": Attacking Infector at position 1/1")
            self._move_and_attack((30, 15), Config().char["atk_len_diablo_infector"] * 0.3)
            self._move_and_attack((-30, -15), Config().char["atk_len_diablo_infector"] * 0.3)
            self._move_and_attack((30, 15), Config().char["atk_len_diablo_infector"] * 0.3)
            self._move_and_attack((30, -15), Config().char["atk_len_diablo_infector"] * 0.4)
            wait(0.1, 0.15)
            self._move_and_attack((30, 15), Config().char["atk_len_diablo_infector"] * 0.3)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif seal_layout == "C2-G":
            # NOT killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals his attack sequence can be found in C2-G_seal2
            Logger.debug(seal_layout + ": No need for attacking Infector at position 1/1 - he was killed during clearing the seal")

        else:
            Logger.warning(seal_layout + ": Invalid location for kill_infector("+ seal_layout +"), should not happen.")
            return False
        return True


    def kill_diablo(self) -> bool:
        ### APPROACH ###
        ### ATTACK ###
        pos_m = convert_abs_to_monitor((0, 0))
        # mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        Logger.debug("Attacking Diablo at position 1/1")

        self._move_and_attack((60, 30), Config().char["atk_len_diablo"])
        self._move_and_attack((-60, -30), Config().char["atk_len_diablo"])
        self._move_and_attack((60, 30), Config().char["atk_len_diablo"])
        self._move_and_attack((-60, -30), Config().char["atk_len_diablo"])
        self._move_and_attack((60, 30), Config().char["atk_len_diablo"])
        self._move_and_attack((-60, -30), Config().char["atk_len_diablo"])
        wait(0.1, 0.15)
        self._move_and_attack((60, 30), Config().char["atk_len_diablo"])
        self._move_and_attack((-60, -30), Config().char["atk_len_diablo"])
        ### LOOT ###
        self._picked_up_items |= self._pickit.pick_up_items(self)
        return True

    ########################################################################################
    # Chaos Sanctuary, Trash, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
    ########################################################################################

    def kill_cs_trash(self, location:str) -> bool:

        ###########
        # SEALDANCE
        ###########

        if location == "sealdance": #if seal opening fails & trash needs to be cleared -> used at ANY seal
            ### APPROACH
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                # #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        ################
        # CLEAR CS TRASH
        ################

        elif location == "rof_01": #node 603 - outside CS in ROF
            ### APPROACH ###
            if not self._pather.traverse_nodes([603], self, timeout=3): return False #calibrate after static path
            pos_m = convert_abs_to_monitor((0, 0))
            ### ATTACK ###
            wait(1)#give merc the chance to activate holy freeze
            #print("mercwait")
            if not Config().char['cs_mob_detect'] or get_visible_targets():

                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([603], self): return False #calibrate after looting


        elif location == "rof_02": #node 604 - inside ROF
            ### APPROACH ###
            if not self._pather.traverse_nodes([604], self, timeout=3): return False  #threshold=0.8 (ex 601)
            ### ATTACK ###
            wait(1)#give merc the chance to activate holy freeze
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance_hall_01": ##static_path "diablo_entrance_hall_1", node 677, CS Entrance Hall1
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("diablo_entrance_hall_1", self) # 604 -> 671 Hall1
            ### ATTACK ###
            wait(1)#give merc the chance to activate holy freeze
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance_hall_02":  #node 670,671, CS Entrance Hall1, CS Entrance Hall1
            ### APPROACH ###
            if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
            self._pather.traverse_nodes_fixed("diablo_entrance_1_670_672", self) # 604 -> 671 Hall1
            if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
            #Move to Layout Check
            if not self._pather.traverse_nodes([671], self): return False # calibrate before static path
            self._pather.traverse_nodes_fixed("diablo_entrance_hall_2", self) # 671 -> LC Hall2



        # TRASH LAYOUT A

        elif location == "entrance1_01": #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([673], self): return False # , timeout=3): # Re-adjust itself and continues to attack

        elif location == "entrance1_02": #node 673
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
            self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) # Moves char to postion close to node 674 continues to attack
            if not self._pather.traverse_nodes([674], self): return False#, timeout=3)

        elif location == "entrance1_03": #node 674
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
                self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([675], self): return False#, timeout=3) # Re-adjust itself
            self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) #static path to get to be able to spot 676
            if not self._pather.traverse_nodes([676], self): return False#, timeout=3)

        elif location == "entrance1_04": #node 676- Hall3
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-50, -150), Config().char["atk_len_cs_trashmobs"])
                self._move_and_attack((50, 150), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        # TRASH LAYOUT B

        elif location == "entrance2_01": #static_path "diablo_entrance_hall_2"
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_02": #node 682
            ### APPROACH ###
            #if not self._pather.traverse_nodes([682], self): return False # , timeout=3):
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_right", self) #pull mobs from the right
            wait (0.2, 0.5)
            if not self._pather.traverse_nodes([605], self): return False#, timeout=3)
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_03": #node 683
            ### APPROACH ###
            #if not self._pather.traverse_nodes([682], self): return False # , timeout=3):
            #self._pather.traverse_nodes_fixed("diablo_entrance2_1", self)
            #if not self._pather.traverse_nodes([683], self): return False # , timeout=3):
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top1", self) #pull mobs from top
            wait (0.2, 0.5)
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top2", self) #pull mobs from top
            if not self._pather.traverse_nodes([605], self): return False#, timeout=3)
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_04": #node 686 - Hall3
            ### APPROACH ###
            if not self._pather.traverse_nodes([605], self): return False#, timeout=3)
            #if not self._pather.traverse_nodes([683,684], self): return False#, timeout=3)
            #self._pather.traverse_nodes_fixed("diablo_entrance2_2", self)
            #if not self._pather.traverse_nodes([685,686], self): return False#, timeout=3)
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_hall3", self)
            if not self._pather.traverse_nodes([609], self): return False#, timeout=3)
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall3_pull_609", self)
            if not self._pather.traverse_nodes([609], self): return False#, timeout=3)
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((0, 0), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-50, -150), Config().char["atk_len_cs_trashmobs"] * 0.5)
                self._move_and_attack((50, 150), Config().char["atk_len_cs_trashmobs"] * 0.2)
                self._move_and_attack((250, -150), Config().char["atk_len_cs_trashmobs"] * 0.5)
                self._move_and_attack((-250, -150), Config().char["atk_len_cs_trashmobs"] * 0.2)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
                self._picked_up_items |= self._pickit.pick_up_items(self)
                if not self._pather.traverse_nodes([609], self): return False#, timeout=3)
                self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([609], self): return False#, timeout=3)

        ####################
        # PENT TRASH TO SEAL
        ####################

        elif location == "dia_trash_a": #trash before between Pentagramm and Seal A Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -100), Config().char["atk_len_cs_trashmobs"])
                self._move_and_attack((30, 100), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "dia_trash_b": #trash before between Pentagramm and Seal B Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -100), Config().char["atk_len_cs_trashmobs"])
                self._move_and_attack((30, 100), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "dia_trash_c": ##trash before between Pentagramm and Seal C Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"])
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -100), Config().char["atk_len_cs_trashmobs"])
                self._move_and_attack((30, 100), Config().char["atk_len_cs_trashmobs"])
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        ###############
        # LAYOUT CHECKS
        ###############

        elif location == "layoutcheck_a": #layout check seal A, node 619 A1-L, node 620 A2-Y
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
            #Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "layoutcheck_b": #layout check seal B, node 634 B1-S, node 649 B2-U
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "layoutcheck_c": #layout check seal C, node 656 C1-F, node 664 C2-G
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        ##################
        # PENT BEFORE SEAL
        ##################

        elif location == "pent_before_a": #node 602, pentagram, before CTA buff & depature to layout check - not needed when trash is skipped & seals run in right order
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "pent_before_b": #node 602, pentagram, before CTA buff & depature to layout check
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "pent_before_c": #node 602, pentagram, before CTA buff & depature to layout check
            ### APPROACH ###
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        ###########
        # SEAL A1-L
        ###########

        elif location == "A1-L_01":  #node 611 seal layout A1-L: safe_dist
            ### APPROACH ###
            if not self._pather.traverse_nodes([611], self): return False # , timeout=3):
            ### ATTACK ###
            wait(1)#give merc the chance to activate holy freeze
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_02":  #node 612 seal layout A1-L: center
            ### APPROACH ###
            if not self._pather.traverse_nodes([612], self): return False # , timeout=3):
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                #self._cast_hammers(0.5, "cleansing")
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_03":  #node 613 seal layout A1-L: fake_seal
            ### APPROACH ###
            if not self._pather.traverse_nodes([613], self): return False # , timeout=3):
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                #self._cast_hammers(0.5, "cleansing")
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "A1-L_seal1":  #node 613 seal layout A1-L: fake_seal
            ### APPROACH ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([614], self): return False
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_seal2":  #node 614 seal layout A1-L: boss_seal
            ### APPROACH ###
            if not self._pather.traverse_nodes([613, 615], self): return False # , timeout=3):
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss

        ###########
        # SEAL A2-Y
        ###########

        elif location == "A2-Y_01":  #node 622 seal layout A2-Y: safe_dist
            ### APPROACH ###
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.debug("A2-Y: Hop!")
            #if not self._pather.traverse_nodes([622], self): return False # , timeout=3):
            if not self._pather.traverse_nodes([622], self): return False
            wait(1)#give merc the chance to activate holy freeze
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                ### ATTACK ###
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
            ### LOOT ###
            # we loot at boss

        elif location == "A2-Y_02":  #node 623 seal layout A2-Y: center
            ### APPROACH ###
            # if not self._pather.traverse_nodes([623,624], self): return False #
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
            ### LOOT ###
            # we loot at boss

        elif location == "A2-Y_03": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "A2-Y_seal1":  #node 625 seal layout A2-Y: fake seal
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            if not self._pather.traverse_nodes([625], self): return False # , timeout=3):

        elif location == "A2-Y_seal2":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues

        ###########
        # SEAL B1-S
        ###########

        elif location == "B1-S_01":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B1-S_02":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B1-S_03":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B1-S_seal2": #B only has 1 seal, which is the boss seal = seal2
            ### APPROACH ###
            if not self._pather.traverse_nodes([634], self): return False # , timeout=3):
            ### ATTACK ###
            ### LOOT ###


        ###########
        # SEAL B2-U
        ###########

        elif location == "B2-U_01":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B2-U_02":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B2-U_03":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B2-U_seal2": #B only has 1 seal, which is the boss seal = seal2
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self)
            if not self._pather.traverse_nodes([644], self): return False # , timeout=3):
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss


        ###########
        # SEAL C1-F
        ###########

        elif location == "C1-F_01":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C1-F_02":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C1-F_03":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C1-F_seal1":
            ### APPROACH ###
            wait(0.1,0.3)
            self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self)
            wait(0.1,0.3)
            if not self._pather.traverse_nodes([655], self): return False # , timeout=3):
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
                if not self._pather.traverse_nodes([655], self): return False # , timeout=3):

        elif location == "C1-F_seal2":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
            if not self._pather.traverse_nodes([652], self): return False # , timeout=3):
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
                if not self._pather.traverse_nodes([652], self): return False # , timeout=3):

        ###########
        # SEAL C2-G
        ###########

        elif location == "C2-G_01": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C2-G_02": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C2-G_03": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C2-G_seal1":
            ### APPROACH ###
            #if not self._pather.traverse_nodes([663, 662], self): return False # , timeout=3): #caused 7% failed runs, replaced by static path.
            self._pather.traverse_nodes_fixed("dia_c2g_lc_661", self)
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")
            """
            pos_m = convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
            #self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            """

        elif location == "C2-G_seal2":
            ### APPROACH ###
            # Killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals
            seal_layout="C2-G"
            self._pather.traverse_nodes_fixed("dia_c2g_663", self)
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                Logger.debug(seal_layout + ": Attacking Infector at position 1/1")
                #self._cast_hammers(Config().char["atk_len_diablo_infector"])
                #self._cast_hammers(0.8, "redemption")
                self._move_and_attack((30, 15), Config().char["atk_len_diablo_infector"])
                #self._cast_hammers(0.8, "redemption")
                self._move_and_attack((30, -15), Config().char["atk_len_diablo_infector"])
                wait(0.1, 0.15)
                #self._cast_hammers(1.2, "redemption")
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([664, 665], self): return False # , timeout=3):

        else:
            ### APPROACH ###
            Logger.warning("I have no location argument given for kill_cs_trash(" + location + "), should not happen. Throwing some random hammers")
            ### ATTACK ###
            if not Config().char['cs_mob_detect'] or get_visible_targets():
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                self._move_and_attack((30, 15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                #self._cast_hammers(0.75, "redemption")
                self._move_and_attack((-30, -15), Config().char["atk_len_cs_trashmobs"] * 0.5)
                ### LOOT ###
                self._picked_up_items |= self._pickit.pick_up_items(self)
        return True
