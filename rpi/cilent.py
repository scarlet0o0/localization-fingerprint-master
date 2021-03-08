
import socket
import common
import time

def server2(q):
    cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting to...', common.server_ip, common.server_port)
    cli_socket.connect((common.server_ip, common.server_port))
    print('Connected to the server...')

    while True:
        msgFromClient = cli_socket.recv(common.BUF_SIZE).decode('utf-8')
        print(msgFromClient)
        id = msgFromClient.split(' ')[0]
        x = int(msgFromClient.split(' ')[1])
        y = int(msgFromClient.split(' ')[2])
        print(id)
        print(x)
        print(y)
        q.put(id)
        q.put(x)
        q.put(y)
        time.sleep(common.sleep_sec)