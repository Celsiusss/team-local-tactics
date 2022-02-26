from socket import AF_INET, SO_REUSEADDR, SOCK_STREAM, gethostname, socket
from ssl import SOL_SOCKET
from time import sleep

from constants import B_DONE, B_INPUT, B_MESSAGE

def send_to_player(num, message):
    psockets[num].send(B_MESSAGE + message.encode() + B_DONE)

def send_to_all(message):
    for sock in psockets:
        sock.send(B_MESSAGE + message.encode() + B_DONE)

def request_input(num):
    psockets[num].send(B_INPUT)
    return recieve_from(num)

def recieve_from(num):
    while True:
        data = psockets[num].recv(1024)
        if data:
            return data.decode()

psockets = []


sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

sock.bind(('localhost', 1200))

sock.listen()

while True:
    (cs, ip) = sock.accept()
    cs.send(B_MESSAGE + 'Connectedaaaa'.encode() + B_DONE)
    psockets.append(cs)
    send_to_player(0, 'Yoyoyoyo')
    print(request_input(0))
    sleep(2)
    send_to_all('lmao')
    cs.close()
    



