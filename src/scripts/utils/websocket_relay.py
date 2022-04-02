import time
import json
import threading
import requests
from websocket import create_connection
import re
from bot_info import BOT_DATA
from bot_events import hook

def external_ip():
    """
        even with all these websites.. one day this function will just not work :'(
    """
    return "204.210.155.70"
    websites = ["https://api.ipify.org", "https://icanhazip.com", "https://ifconfig.me/ip", "https://ipecho.net/plain", "https://ident.me"]
    for website in websites:
        try:
           ip = requests.get(website).content.decode('utf8')
           if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                return ip
        except:
            pass

"""
    This class can be taken advantage of to:
        Recieve and send messages to a website.
        Recieve and send messages to other bots.
        
"""

class WebSocketClient():
    def __init__(self, webserver_type, port):
        self.domain = "{}:{}"
        if webserver_type == 1:
            self.domain = self.domain.format("127.0.0.1", port)
        elif webserver_type == 2:
            self.domain = self.domain.format(external_ip(), port)
        print(self.domain)
        sid = json.loads(requests.get(f"http://{self.domain}/socket.io/?EIO=4&transport=polling&t=N_JEvOY").text[1:])['sid']
        requests.post(f"http://{self.domain}/socket.io/?EIO=4&transport=polling&t=N_JEvOZ&sid={sid}", data="40")

        self.ws = create_connection(f"ws://{self.domain}/socket.io/?EIO=4&transport=websocket&sid={sid}")
        self.ws.send('2probe')
        self.ws.send('5')

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
            if msg == "2": # ping
                self.ws.send('3') # pong
            elif "website.request" in msg:
                msg = json.loads(json.loads(msg[2:])[1])
                hook.Call("recv_website_request", message=msg)
                
    
    def send(self, msg: object):
        msg["from"] = "python_botty"
        msg["id"] = self.id
        data = json.dumps(msg).replace('"', '\\"')
        self.ws.send('42["message", "{}"]'.format(data))
    
    # def update(self, data: object):
    #     self.update_queue.append(data)

    def _update(self):
        while True:
            time.sleep(1)
            if len(self.update_queue) > 0:
                self.send(self.update_queue.pop(0))

