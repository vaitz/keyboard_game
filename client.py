import socket
import struct
import select
from pynput.keyboard import Listener


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


def on_press(key):
    pass


def on_release(key):
    print(key)
    client_tcp.sendall(key.char.encode())


# CLIENT MODES:
# Looking for a server
def lookup_server(client_udp):
    server_ip, server_port = '', 0
    while True:
        data, address = client_udp.recvfrom(1024)
        (ip, port) = address
        server_ip = ip
        # try catch???
        (magic_cookie, msg_type, server_port) = struct.unpack('Ibh', data)
        magic_cookie = hex(magic_cookie)
        msg_type = hex(msg_type)
        # print(magic_cookie, msg_type, server_port)
        # check the UDP message format
        if magic_cookie != '0xfeedbeef' or msg_type != '0x2':
            print(bcolors.WARNING + "UDP message not in format!" + bcolors.ENDC)
            continue

        # need to check if there are more data after the port???????????????????????
        print("Received offer from " + ip + ", attempting to connect...")
        break
    return server_ip, server_port


# Connecting to a server
def connect(server_ip, server_port, client_tcp):
    # socket.settimeout() ?? if not accepted
    try:
        client_tcp.connect((server_ip, server_port))
        client_tcp.sendall('Team1\n'.encode())
        return True
    except ConnectionError:
        return False


# Game mode
def game(client_tcp):
    # start game
    data = client_tcp.recv(1024)
    print(data.decode())

    # ?????
    with Listener(on_press=on_press, on_release=on_release) as listener:  # Create an instance of Listener
        # listener.join()
        while True:
            # end game
            data = client_tcp.recv(1024)
            print(data.decode())
            listener.stop()
            break


    print("Server disconnected, listening for offer requests...")


print(bcolors.OKGREEN + "Client started, listening for offer requests..." + bcolors.ENDC)
while True:
    # create UDP socket for lookup
    client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)# Enable broadcasting mode
    client_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_udp.bind(("", BROADCAST_PORT))
    server_ip, server_port = lookup_server(client_udp)
    client_udp.close()
    # create TCP socket for lookup
    client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # take care of case that connect to bad server or connection failed
    ans = connect(server_ip, server_port, client_tcp)
    if ans:
        game(client_tcp)
    client_tcp.close()



