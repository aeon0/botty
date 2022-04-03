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
    websites = ["https://api.ipify.org", "https://icanhazip.com", "https://ifconfig.me/ip", "https://ipecho.net/plain", "https://ident.me"]
    for website in websites:
        try:
           ip = requests.get(website).content.decode('utf8')
           if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                return ip
        except:
            pass


class WebSocketClient():
    def __init__(self, webserver_type, port):
        self.domain = "{}:{}"
        
        if webserver_type == 1:
            self.domain = self.domain.format("127.0.0.1", port)
        elif webserver_type == 2:
            self.domain = self.domain.format(external_ip(), port)

        sessionid = json.loads(requests.get(f"http://{self.domain}/socket.io/?EIO=4&transport=polling&t=N_JEvOY").text[1:])['sid']
        requests.post(f"http://{self.domain}/socket.io/?EIO=4&transport=polling&t=N_JEvOZ&sid={sessionid}", data="40")

        self.ws = create_connection(f"ws://{self.domain}/socket.io/?EIO=4&transport=websocket&sid={sessionid}")
        self.ws.send('2probe')
        self.ws.send('5')

        self.sessionid = None # this session id will be different than the one that is getting used above.
        self.message_queue = []

    def run(self):
        self.listen_thread = threading.Thread(target=self._listen)
        self.update_thread = threading.Thread(target=self._update)
        
        self.listen_thread.start()
        self.update_thread.start()
        
    
    def send(self, msg: object, isJson=True):
        if isJson:
            msg["from"] = "python_botty"
            msg["id"] = self.sessionid
            data = json.dumps(msg).replace('"', '\\"')
            self.ws.send(f'42["message", "{data}"]')
        else:
            self.ws.send(f'42["message", "{msg}"]')
    

    def _listen(self):
        while True:
            time.sleep(1)
            msg = self.ws.recv()
            if msg == "2": # ping
                self.ws.send('3') # pong
            elif '40{"sid":"' in msg: # Get the session id that the server is giving us
                self.sessionid = json.loads(msg[2:])['sid']
            elif "website.request" in msg: # This is the message that the website is sending us
                msg = json.loads(json.loads(msg[2:])[1])
                hook.Call("recv_website_request", message=msg)
                
    def _update(self):
        while True:
            time.sleep(1)
            if len(self.message_queue) > 0:
                self.send(self.message_queue.pop(0))

