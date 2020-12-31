import socket
import struct
import select
from pynput.keyboard import Listener


# Class for pretty colors prints
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



BROADCAST_PORT = 13117

# Press keys handlers
def on_press(key):
    pass


def on_release(key):
    print(key)
    # try:
    client_tcp.sendall(key.char.encode())
    # except ConnectionError:
    #     pass
    # except OSError:
    #     pass

# CLIENT MODES:
# Looking for a server
def lookup_server(client_udp):
    server_ip, server_port = '', 0
    while True:
        # search for broadcast
        data, address = client_udp.recvfrom(1024)
        (ip, port) = address
        server_ip = ip
        # try to unpack the message
        try:
            (magic_cookie, msg_type, server_port) = struct.unpack('Ibh', data)
        except struct.error:
            continue
        magic_cookie = hex(magic_cookie)
        msg_type = hex(msg_type)

        # check the UDP message format
        if magic_cookie != "0xfeedbeef" or msg_type != "0x2" or server_port < 0:
            continue

        print(bcolors.OKGREEN + "Received offer from " + ip + ", attempting to connect..."+ bcolors.ENDC)
        break
    return server_ip, server_port


# Connecting to a server
def connect(server_ip, server_port, client_tcp):
    # try:
        client_tcp.connect((server_ip, server_port))
        client_tcp.sendall('Key2Pay\n'.encode())
        return True
    # except ConnectionError:
    #     return False


# Game mode
def game(client_tcp):
    # waiting for start game message
    data = client_tcp.recv(1024)
    print(data.decode())

    # thread listener, recives characters input from the user
    with Listener(on_press=on_press, on_release=on_release) as listener:  
        # waiting for end game message and stop listening to typing
        data = client_tcp.recv(1024)
        print(data.decode())
        listener.stop()

    print("Server disconnected, listening for offer requests...")

# Client's main loop - waiting, connect, game
print(bcolors.OKGREEN + "Client started, listening for offer requests..." + bcolors.ENDC)
while True:
    # create UDP socket for lookup
    client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)# Enable broadcasting mode
    client_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_udp.bind(("", BROADCAST_PORT))

    # waiting mode
    server_ip, server_port = lookup_server(client_udp)
    client_udp.close()
    
    # create TCP socket for lookup
    client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # take care of case that connect to bad server or connection failed
    # client_tcp.settimeout(10)
    # try:
    ans = connect(server_ip, server_port, client_tcp)
    if ans:
        game(client_tcp)
    client_tcp.close()
    # except socket.timeout:
    #     pass
    # except ConnectionError:
    #     pass



