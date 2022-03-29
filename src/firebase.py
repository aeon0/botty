import pyrebase
from datetime import datetime, timedelta
from config import Config
import random
import string
import time

class Firebase:
    firebaseConfig = {
      "apiKey": "AIzaSyC_uqKgwFcT6HgqdSvfCOubK8M0xx5L4nM",
      "authDomain": "botty-eaff2.firebaseapp.com",
      "databaseURL": "https://botty-eaff2-default-rtdb.europe-west1.firebasedatabase.app",
      "projectId": "botty-eaff2",
      "storageBucket": "botty-eaff2.appspot.com",
      "messagingSenderId": "868389370365",
      "appId": "1:868389370365:web:6030a7f6d1bff804778194"
    }
    
    runtime = {
        "run_trav":"60",
        "run_pindle":"45",
        "run_eldritch":"30",
        "run_shenk":"30",
        "run_nihlathak":"90",
        "run_tower":"120",
        "run_arcane":"120",
        "run_diablo":"240",
        "run_andy":"90",
        "run_meph":"90",
        "run_baal":"300",
        "run_pit":"90",
        "run_stony_tomb":"90",
        "run_cows": "300"    
    }
    
    def __init__(self):
        firebase = pyrebase.initialize_app(self.firebaseConfig)
        self.db = firebase.database()
        self.config = Config ()
        self.routelist =[]
        self.runt = 0
        self.get_routelist_runtime ()
        self._gn=""
        self._pw=""
        self._last_update = datetime.utcnow()
        self.cont = False
        self._first_game = True
        self._auth = firebase.auth()
        self._user = self._auth.sign_in_with_email_and_password(self.config.general["db_email"], self.config.general["db_password"])
        self._last_auth = datetime.utcnow()
        
         

    def remove_inactive_users (self, group, now, delta):
        for key, value in group.val()["shared_with"].items():
            if now - datetime.strptime (value, "%m/%d/%Y, %H:%M:%S") > delta:
                groupID = group.key()
                self.db.child ("regions").child(self.config.general["region"]).child ("groups").child(groupID).child ("shared_with").child (key).remove(self._user['idToken'])   
                self.db.child("regions").child(self.config.general["region"]).child ("groups").child (groupID).child ("claimed_runs").child (key).remove(self._user['idToken'])
        pass
    def delete_old_games(self):
        """
        function to delete all runs that arent been updated for a certain amount of time

        """
        now= datetime.utcnow()
        delta = timedelta (minutes=10)
        groups = self.db.child ("regions").child(self.config.general["region"]).child ("groups").get(self._user['idToken'])
        print (groups)
        if groups.pyres != None:
            for group in groups.each():
                last_update = datetime.strptime (group.val()["last_update"], "%m/%d/%Y, %H:%M:%S")
                if now - last_update > delta:
                    #Games that havent been updated for 10 mins
                    groupID = group.key()
                    self.db.child ("regions").child(self.config.general["region"]).child ("groups").child(groupID).remove(self._user['idToken'])
                else:
                    self.remove_inactive_users (group, now, delta)

    def get_routelist_runtime (self):
        for key, value in self.config.routes.items():
            if value:
                self.routelist.append (key)
                self.runt += int (self.runtime [key])
        
    
    def add_group (self, Name:str, Password:str, userID:str):
        """
        function to add a new group if no group is matching specifired params
        """
        routes ={"userID":userID}
        id = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
        now= datetime.utcnow()
        
        routes ={userID : self.routelist}   
        group_data = {
                    "name": Name,
                    "password": Password,
                    "shared_with": {userID : now.strftime("%m/%d/%Y, %H:%M:%S")},
                    "claimed_runs":routes,
                    "last_update": now.strftime("%m/%d/%Y, %H:%M:%S"),
                    "approx_runtime": str (self.runt)
        } 
        self.db.child("regions").child(self.config.general["region"]).child ("groups").child (id).set (group_data, self._user['idToken'])
        return id
    
    def update_group_data (self, gameID, userID, Name:str ="", Password:str =""):
        """
        function to update gamename, password and timestamp
        """
        now= datetime.utcnow()
        #Update timestamp for user
        self.db.child("regions").child(self.config.general["region"]).child ("groups").child (gameID).child ("shared_with").update ({userID: now.strftime("%m/%d/%Y, %H:%M:%S")}, self._user['idToken'])
        #Update GN/PW and last_update
        if Name!="":
            self.db.child("regions").child(self.config.general["region"]).child ("groups").child (gameID).update ({"name": Name}, self._user['idToken'])
            self.db.child("regions").child(self.config.general["region"]).child ("groups").child (gameID).update ({"password": Password}, self._user['idToken'])
            self.db.child("regions").child(self.config.general["region"]).child ("groups").child (gameID).update ({"last_update": now.strftime("%m/%d/%Y, %H:%M:%S")}, self._user['idToken'])    

    def group_valid(self, group):
        if len(group.val()["shared_with"]) < self.config.general["max_players"]:
            if abs(self.runt - int (group.val()["approx_runtime"])) < int (self.config.general["max_delta_approx_time"]): 
                for user,runs in group.val()["claimed_runs"].items():
                    for run in runs:
                        for route in self.routelist:
                            if route in run:
                                return False
                return True 
        return False   


    def select_group(self, userID):
        """
        function to add user and runtype to group
        #TODO add support for given groupID
        """
        now= datetime.utcnow()
        groups = self.db.child ("regions").child(self.config.general["region"]).child ("groups").get(self._user['idToken'])
        if groups.pyres != None:
            for group in groups.each():
                valid = self.group_valid (group)
                if valid:
                    gameID = group.key()
                    self.db.child("regions").child(self.config.general["region"]).child ("groups").child (gameID).child ("shared_with").update ({userID: now.strftime("%m/%d/%Y, %H:%M:%S")}, self._user['idToken'])
                    self.db.child("regions").child(self.config.general["region"]).child ("groups").child (gameID).child ("claimed_runs").update ({userID: self.routelist}, self._user['idToken'])
                    if group != False:
                        #self._groupID = group.key()
                        self._gn = group.val()["name"]
                        self._pw = group.val()["password"]
                    return group
        return False
    
    def stream_handler(self, message):
        print(message["event"]) # put
        print(message["path"]) # /-K7yGTTEp7O549EzTYtI
        print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
        delta = timedelta (minutes=50)
        if datetime.utcnow () > delta + self._last_auth:
            self._user = self._auth.refresh(self._user['refreshToken'])
        if message["event"] in ["put", "patch"]:
            for key, val in message ["data"].items():
                if key == "name":
                    self._gn = val
                elif key == "password":
                    self._pw = val
                elif key == "last_update":
                    if self._last_update < datetime.strptime (val, "%m/%d/%Y, %H:%M:%S"):
                        self._last_update = datetime.strptime (val, "%m/%d/%Y, %H:%M:%S") 
                        self.cont = True
        
        
                
                
                            
                                 
    def init_stream():
        """
        function to subscribe to special group
        """
        
if __name__ == "__main__":
    cfg = Config ()
    firebase = Firebase ()
    #firebase.db.child("regions").child("europe").child ("groups").set (test_data)
    #id = firebase.add_group ("Game", "Password", "123456")
    #firebase.update_game ("9VjHZXZ33V", "456789")
    #firebase.delete_old_games ()
    firebase.update_group_data ("WIjfEgI8yg", "sp6eG6Gl7W", "test123", "456")