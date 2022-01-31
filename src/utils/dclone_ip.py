import psutil
from config import Config
from messages import Messenger

def get_d2r_game_ip():
    config = Config()
    blacklist_ip = ["127.0.0.1", "34.117", "137.221", "37.244", "117.52"]
    region_ips = []
    for tmp in config.dclone["region_ips"].split(","):
        region_ips.append(tmp.strip())
    for proc in psutil.process_iter():
        if proc.name() == "D2R.exe":
            D2R_pid = proc.pid
    for connection in psutil.net_connections():
        if connection.status == "ESTABLISHED" and connection.pid == D2R_pid and connection.raddr[1] == 443:
            if not any(tmp in connection.raddr[0] for tmp in blacklist_ip):
                return connection.raddr[0]
            if any(tmp in connection.raddr[0] for tmp in region_ips):
                return connection.raddr[0]
    return "Unknown game server"

def get_d2r_game_server_region_by_ip(ip):
    us_server = ["158.115.222", "158.115.221"] 
    eu_server = ["37.244.11", "37.244.48"] 
    asia_server = ["34.92"] 
    asia_mumbai = ["34.93", "35.200", "35.244"] 
    us_sao_paolo = ["34.95", "35.198", "35.199", "35.247"] 
    asia_jakarta = ["34.101"]
    if any(tmp in ip for tmp in us_server):
        return "Us Server"
    if any(tmp in ip for tmp in eu_server):
        return "Eu Server"
    if any(tmp in ip for tmp in asia_mumbai):
        return "Asia Mumbai Server"
    if any(tmp in ip for tmp in us_sao_paolo):
        return "Us Sao Paolo Server"
    if any(tmp in ip for tmp in asia_jakarta):
        return "Asia Jakarta Server"
    if any(tmp in ip for tmp in asia_server):
        return "Asia Server"
    if ip == "Unknown game server":
        return "Unknown Server"
    else:
        return "Blizzard Server"
            
if __name__ == "__main__":
    config = Config()
    messenger = Messenger()
    if config.dclone["region_ips"] != "" and config.dclone["dclone_hotip"] != "":
        print(f"Current Game IP: {get_d2r_game_ip()}")
        print(f"Current Game Server: {get_d2r_game_server_region_by_ip(get_d2r_game_ip())}")
        messenger.send_message(f"Dclone IP Found on {get_d2r_game_server_region_by_ip(get_d2r_game_ip())} on IP: {get_d2r_game_ip()}")
    else:
        print(f"Please Enter the region ip and hot ip on config to use")