import time
import json
import threading
import requests
from websocket import create_connection

from bot_info import BOT_DATA



class WebSocketClient():
    def __init__(self):
        sid = json.loads(requests.get("http://192.168.0.3:5000/socket.io/?EIO=4&transport=polling&t=N_JEvOY").text[1:])['sid']
        requests.post("http://192.168.0.3:5000/socket.io/?EIO=4&transport=polling&t=N_JEvOZ&sid={}".format(sid), data="40")

        self.ws = create_connection("ws://192.168.0.3:5000/socket.io/?EIO=4&transport=websocket&sid={}".format(sid))
        self.ws.send('2probe')
        self.ws.send('5')
        self.send(BOT_DATA)

        self.id = sid
        self.passive_update_delay = 10 # how long to wait in seconds between sending automatic updates to the websocket
        self.update_queue = []

    def run(self):
        self.listen_thread = threading.Thread(target=self.listen)
        self.update_thread = threading.Thread(target=self._update)
        
        self.listen_thread.start()
        self.update_thread.start()
        
    
    def listen(self):
        while True:
            time.sleep(1)
            msg = self.ws.recv()
            print(msg)
            if msg == "2": # ping
                self.ws.send('3') # pong
            elif "function" in msg:
                print('MSG', msg)

                msg = json.loads(json.loads(msg[2:])[1])
                if msg.get("function") == "update":
                    self.send(BOT_DATA)
    
    def send(self, msg: object):
        print("SENT!")
        data = json.dumps(msg).replace('"', '\\"')
        self.ws.send('42["message", "{}"]'.format(data))
    
    def update(self, data: object):
        self.update_queue.append(data)

    def _update(self):
        now = time.time()
        while True:
            time.sleep(1)
            if time.time() > now + self.passive_update_delay:
                print(1343232432423)

                BOT_DATA["id"] = self.id
                self.update_queue.append(BOT_DATA)
                now = time.time()

            if len(self.update_queue) > 0:
                self.send(self.update_queue.pop(0))


ws = WebSocketClient()
ws.run()