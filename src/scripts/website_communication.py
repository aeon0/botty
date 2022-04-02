from bot_info import BOT_DATA
from scripts.utils.websocket_relay import WebSocketClient
from config import Config
from bot_events import hook
from game_controller import GameController

# webserver_type = Config().webserver["enable"] # 0 = disabled, 1 = local, 2 = remote 
# webserver_port = Config().webserver["port"] # port to listen on

if True:# or webserver_type == 1 or webserver_type == 2:
    ws = WebSocketClient(2, 5000)
    ws.run()
    print(ws.id)

    def send_update():
        copy = BOT_DATA.copy()
        copy["action"] = "update"
        ws.send(copy)

    def do_action(message):
        if ws.id in message["ids"]:
            if message["action"] == "update":
                    send_update()
            elif message["action"] == "pause" or message["action"] == "resume":
                GameController.bot.toggle_pause()

        

    hook.Add("on_bot_init", "WEBSITE_init_send_BOTDATA", send_update)
    hook.Add("on_run", "WEBSITE_run_send_BOTDATA", send_update)
    hook.Add("on_pause", "WEBSITE_pause_send_BOTDATA", send_update)
    hook.Add("on_resume", "WEBSITE_resume_send_BOTDATA", send_update)


    hook.Add("recv_website_request", "WEBSITE_recieve_request", do_action)