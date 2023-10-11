#!/usr/bin/python                                                                                                                                                      
import socket
from threading import Thread
import sys
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("255.255.255.255", 80))
    return s.getsockname()[0]

try:
    HOST = get_ip_address()
    PORT = int(sys.argv[1])
    CLIENTS_BUFF = 5
except:
    print("Specify port as first argument")
    quit(1)

def user_handler(connected_users, socket, address) -> None:
    socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket.send(bytes('Write your nickname >> ', 'utf-8'))
    user_input = socket.recv(1024)
    name = '{} ({})'.format(user_input.decode()[:-1], address) if user_input != b'\n' else address
    while True:
        msg = socket.recv(1024)
        if msg == b'':
            print(name, 'disconnected')
            broadcast_all(connected_users, '', "{} {}".format(name, 'disconnected'), True)
            break
        broadcast_all(connected_users, name, msg.decode()[:-1])
    connected_users.remove(socket)
    socket.close()

def broadcast_all(connected_users, addr, msg, system_msg=False) -> None:
    if not system_msg:
        msg = "{} >> {}".format(addr, msg)
    print(msg)
    for clientsocket in connected_users:
        try:
            clientsocket.send(bytes(msg + "\n", 'utf-8'))
        except:
            continue

def broadcast(is_running, connected_users, hostname) -> None:
    while True:
        try:
            msg = input()
        except EOFError:
            broadcast_all(connected_users, '', 'Host disconnected; Port closed.', True)
            is_running[0] = 0
            return
        if msg == ":q":
            broadcast_all(connected_users, '', 'Host disconnected; Port closed.', True)
            is_running[0] = 0
            return
        elif msg == ":n":
            hostname = msg.split()[1]
            print("{} {}".format("Hostname changed to", hostname))
        broadcast_all(connected_users, hostname, msg)

def main() -> None:
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reuse port if opened
    s.bind((HOST, PORT))
    s.listen(CLIENTS_BUFF)
    
    print("\nCommands:\n   :q to quit\n   :n NEW_HOSTNAME to change hostname")
    print("Port binded; Waiting for users...\n")
    connected_users = []
    
    # Host input handler
    is_running = [1]
    t = Thread(target=broadcast, args=(is_running, connected_users, "HOST"))
    t.start()
    s.settimeout(3)
    while is_running[0]:
        try:
            user_socket, address = s.accept()
        except socket.timeout:
            continue
        connected_users.append(user_socket)
        broadcast_all(connected_users, '', "{} {}".format("Got connection from", address[0]), True)
        t = Thread(target=user_handler, args=(connected_users, user_socket, address[0]))
        t.start()
    s.close()
    return

if __name__ == "__main__":
    print(get_ip_address())
    main()

