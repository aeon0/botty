
from config import Config
from utils.custom_mouse import mouse
from logger import Logger
import time
from firebase import Firebase
import random
import string
from datetime import datetime


class GroupManager:
    def __init__(self, firebase: Firebase):
        self._config = Config()
        self._firebase = firebase
        self._userID = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
        self._groupID = "" 
        self._gn = ""
        self._pw = ""
        self._last_update = datetime.utcnow()
        self._host=False


    def stop_monitor(self):
        self._my_stream.close()

    def set_callback(self, callback):
        self._callback = callback

    def reset_cont_flag(self):
        self._firebase.cont = False
        
    def new_game(self):
        return self._firebase.cont


    def start_monitor(self):
        self._do_monitor = True
        Logger.info("Start Group monitoring")
        self._host = self.decide_host ()
        while self._do_monitor:
            time.sleep (1)   
    
    def decide_host (self)-> bool:
        if self._host == True: 
            return True 
        if self._groupID=="" and Config().general["region"]!="":
            self._firebase.delete_old_games ()
            group = self._firebase.select_group (self._userID)
            if group != False:
                self._groupID = group.key()
                self._gn = group.val()["name"]
                self._pw = group.val()["password"]
                return False
            else:
                return True
        return False
        
    def update_game_data (self):
        if self._groupID!="":
            self._my_stream = self._firebase.db.child("regions").child(self._config.general["region"]).child ("groups").child (self._groupID).stream(self._firebase.stream_handler, self._firebase._user['idToken'])
            #self._gn = self._firebase._gn
            #self._pw = self._firebase._pw
            #self._last_update = self._firebase._last_update
            
        

# Testing:
if __name__ == "__main__":
    keyboard.wait("f11")
    config = Config()
    screen = Screen()
    manager = DeathManager(screen)
    manager.pick_up_corpse(screen)
