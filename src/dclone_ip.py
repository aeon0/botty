# Import for Process Checking - pip install psutil
# Reference: https://psutil.readthedocs.io/en/latest/
import psutil
import re
from config import Config

def get_d2r_game_ip():
    config = Config()
    region_ips = []
    for tmp in config.general["region_ips"].split(","):
        region_ips.append(tmp.strip())

    D2R_pid = ''
    for proc in psutil.process_iter():
        if proc.name() == "D2R.exe":
            D2R_pid = proc.pid
    for connection in psutil.net_connections():
        if connection.status == "ESTABLISHED" and connection.pid == D2R_pid and connection.raddr[1] == 443:
            for validate_ip in region_ips:
                if re.findall(validate_ip, connection.raddr[0]):
                    return connection.raddr[0]

if __name__ == "__main__":
    print(f"Current Game IP: {get_d2r_game_ip()}")