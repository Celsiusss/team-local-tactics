from socket import AF_INET, SO_REUSEADDR, SOCK_STREAM, gethostname, socket
from ssl import SOL_SOCKET

from constants import B_DONE, B_INPUT, B_MESSAGE


sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

sock.bind(('localhost', 1200))

sock.listen()

while True:
    (cs, ip) = sock.accept()
    cs.send(B_MESSAGE + 'Connectedaaaa'.encode() + B_DONE + B_INPUT)
    cs.close()

def send_to_player(num):
    pass

def send_to_all():
    pass

def request_input(num):
    pass

