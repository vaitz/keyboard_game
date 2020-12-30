import socket
import time
import threading
import struct

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


BROADCAST_ADDRESS = "255.255.255.255"
BROADCAST_PORT = 13117
MAGIC_COOKIE = 0xfeedbeef
MSG_TYPE = 0x2
SERVER_PORT = 2034
global list_threads, list_sockets
list_threads = []
list_sockets = []
team_names = []
score_group1 = 0
score_group2 = 0
group1 = []
group2 = []
game_on = False


def udp_broadcast(server_udp):
    stop_time = time.time() + 10
    while time.time() < stop_time:
        data = struct.pack('Ibh', MAGIC_COOKIE, MSG_TYPE, SERVER_PORT)
        server_udp.sendto(data, (BROADCAST_ADDRESS, BROADCAST_PORT))
        print("send")
        time.sleep(1)


def client_thread(client_socket_conn):
    # client_socket_conn.sendall('welcome to the server, send your team name please')
    data = client_socket_conn.recv(1024)
    team_name = data.decode().split('\n')[0]
    print(team_name)
    team_names.append(team_name)

    run = True
    counter = 0
    # game
    try:
        while run:
            if game_on:
                while game_on:
                    data = client_socket_conn.recv(1024)
                    if not data:
                        break
                    print(data.decode())
                    counter += len(data.decode())
        client_socket_conn.close()
    except ConnectionError:
        pass


def tcp_listener(server_tcp):
    stop_time = time.time() + 10
    while time.time() < stop_time:
        (conn, address) = server_tcp.accept()
        ct = threading.Thread(target=client_thread, args=(conn,))
        list_threads.append(ct)
        list_sockets.append(conn)
        ct.run()


# Waiting for clients
def waiting(server_udp, server_tcp):
    # stop_time = time.time() + 10
    T_UDP = threading.Thread(target=udp_broadcast, args=(server_udp,))

    T_TCP = threading.Thread(target=tcp_listener, args=(server_tcp,))
    T_UDP.start()
    T_TCP.start()
    T_TCP.join(10)
    # T_TCP.join()
    # while time.time() < stop_time:
        # accept connections from outside
        # add timeout after 10 seconds without requests?????
        # (conn, address) = server_tcp.accept()
        # ct = threading.Thread(target=client_thread, args=(conn,))
        # list_threads.append(ct)
        # ct.run()

# Game mode
def game(server_tcp):
    print(bcolors.HEADER+"Welcome to Keyboard Spamming Battle Royale"+bcolors.ENDC)
    global score_group1, score_group2, group1, group2, game_on, list_threads, list_sockets
    score_group1 = 0
    score_group2 = 0
    # split to 2 groups
    group1 = []
    group2 = []
    i = 1
    group1_str = ""
    group2_str = ""
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
    for socket in list_sockets:
        try:
            socket.sendall(msg.encode())
        except ConnectionError:
            pass

    game_on = True
    time.sleep(10)
    game_on = False

    # end game msg
    msg_end = "Game over!\nGroup 1 typed in " + str(score_group1) + " characters. Group 2 typed in " \
              + str(score_group2) + " characters."
    if score_group1 > score_group2:
        msg_end += ("\nGroup 1 wins!\nCongratulations to the winners:\n==============================\n" + group1_str)
    else:
        msg_end += ("\nGroup 2 wins!\nCongratulations to the winners:\n==============================\n" + group2_str)
    for socket in list_sockets:
        try:
            socket.sendall(msg_end.encode())
        except ConnectionError:
            pass

    # kill list_threads

    #
    # print(bcolors.HEADER+"Game over!"+bcolors.ENDC)
    # print("Group 1 typed in " + str(group1) + " characters. Group 2 typed in " + str(group2) +  "characters.")
    # if score_group1 > score_group2:
    #     print("Group 1 wins!")
    #     print("Congratulations to the winners:")
    #     print("==============================")
    #     for name in group1:
    #         print(name)
    # else:
    #     print("Group 2 wins!")
    #     print("Congratulations to the winners:")
    #     print("==============================")
    #     for name in group2:
    #         print(name)
    print("Game over, sending out offer requests...")



print(bcolors.OKBLUE + "Server started, listening on IP address 10.100.102.10" + bcolors.ENDC)
while True:
    list_threads = []
    list_sockets = []
    # create UDP socket for broadcast
    server_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # , socket.IPPROTO_UDP)
    server_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Enable broadcasting mode
    # create TCP socket for connecting clients
    server_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_TCP.bind(("10.100.102.10", int(SERVER_PORT)))
    server_TCP.listen()
    waiting(server_UDP, server_TCP)
    server_TCP.close()
    server_UDP.close()
    game(server_TCP)


