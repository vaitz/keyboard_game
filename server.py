import socket
import time
import threading
import struct

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


# Global variables:

# Addresses
name = socket.gethostname()
SERVER_ADDRESS = socket.gethostbyname(name)
BROADCAST_ADDRESS = "255.255.255.255"
SERVER_PORT = 2034

# UDP message format
BROADCAST_PORT = 13117
MAGIC_COOKIE = 0xfeedbeef
MSG_TYPE = 0x2

# Game variables
global list_threads, list_sockets, team_names, game_on
list_threads = []
list_sockets = []
team_names = {}
score_group1 = 0
score_group2 = 0
group1 = []
group2 = []
game_on = False


# UDP broadcast handler - thread
def udp_broadcast(server_udp):
    # ten seconds interval - sends udp message every 1 second
    stop_time = time.time() + 10
    while time.time() < stop_time:
        data = struct.pack('Ibh', MAGIC_COOKIE, MSG_TYPE, SERVER_PORT)
        server_udp.sendto(data, (BROADCAST_ADDRESS, BROADCAST_PORT))
        time.sleep(1)

# TCP clients handler - thread
def client_thread(client_socket_conn):
    # getting the group name
    data = client_socket_conn.recv(1024)
    team_name = data.decode().split('\n')[0]
    team_names[team_name] = 0
    
    # try:
    while True:
        # waiting for the game to start
        while game_on:
            data = client_socket_conn.recv(1024)
            if not data:
                break
            print(data.decode())
            team_names[team_name] = team_names[team_name] + 1
        # time.sleep(1)
    client_socket_conn.close()
    # except ConnectionError:
    #     pass

# TCP handler - thread
def tcp_listener(server_tcp):
    # ten seconds interval - accepting connections and creating thread to each client
    stop_time = time.time() + 10
    while time.time() < stop_time:
        try:
            (conn, address) = server_tcp.accept()
            # conn.settimeout(10)
            ct = threading.Thread(target=client_thread, args=(conn,))
            list_threads.append(ct)
            list_sockets.append(conn)
            ct.run()
        except ConnectionError:
            break
        except socket.timeout:
            break
        except OSError:
            break


# Sending broadcasts and waiting for clients
def waiting(server_udp, server_tcp):
    T_UDP = threading.Thread(target=udp_broadcast, args=(server_udp,))
    T_TCP = threading.Thread(target=tcp_listener, args=(server_tcp,))
    T_UDP.start()
    T_TCP.start()
    # Waits in this line for 10 seconds
    T_UDP.join(10)

# Game mode
def game(server_tcp):
    # initial the game variables
    global score_group1, score_group2, group1, group2, list_threads, list_sockets, game_on
    score_group1 = 0
    score_group2 = 0
    group1 = []
    group2 = []
    i = 1
    group1_str = ""
    group2_str = ""
    # split to 2 groups
    for team in team_names:
        if i % 2 == 0:
            group1.append(team)
            group1_str += team + "\n"
        else:
            group2.append(team)
            group2_str += team + "\n"
        i += 1

    # start game msg
    msg = "Welcome to Keyboard Spamming Battle Royale\nGroup 1:\n=======\n" + group1_str \
          + "Group 2:\n=======\n" + group2_str + "Start pressing keys on your keyboard as fast as you can!!"
    print(msg)
    for socket in list_sockets:
        try:
            socket.sendall(msg.encode())
        except ConnectionError:
            pass
    game_on = True
    # ten seconds for typing
    time.sleep(10)
    game_on = False

    # sums the scores
    for player1 in group1:
        score_group1 += team_names[player1]
    for player2 in group2:
        score_group2 += team_names[player2]

    # end game msg
    msg_end = "Game over!\nGroup 1 typed in " + str(score_group1) + " characters. Group 2 typed in " \
              + str(score_group2) + " characters."
    if score_group1 > score_group2:
        msg_end += ("\nGroup 1 wins!\nCongratulations to the winners:\n==============================\n" + group1_str)
    else:
        msg_end += ("\nGroup 2 wins!\nCongratulations to the winners:\n==============================\n" + group2_str)
    print(msg_end)

    # updating the clients with game summarize
    for socketc in list_sockets:
        try:
            socketc.sendall(msg_end.encode())
            socketc.close()
        except ConnectionError:
            pass

    print(bcolors.OKBLUE + "Game over, sending out offer requests..." + bcolors.ENDC)


# Server's main loop - waiting, game
print(bcolors.OKBLUE + "Server started, listening on IP address " + SERVER_ADDRESS + "" + bcolors.ENDC)
while True:
    # initaial the clients variable
    list_threads = []
    list_sockets = []
    team_names = {}

    # create TCP socket for connecting clients
    server_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_TCP.bind((SERVER_ADDRESS, int(SERVER_PORT)))
    except OSError:
        # time.sleep(1)
        continue

    # create UDP socket for broadcast
    server_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # , socket.IPPROTO_UDP)
    server_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Enable broadcasting mode
    
    server_TCP.listen()
    # server_TCP.settimeout(10)

    waiting(server_UDP, server_TCP)
    server_TCP.close()
    server_UDP.close()

    game(server_TCP)


