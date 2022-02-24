from socket import AF_INET, SOCK_STREAM, socket

from constants import B_DONE, B_INPUT, B_MESSAGE

def send_input(prompt):
    msg = input(prompt)
    sock.send(msg.encode())

sock = socket(AF_INET, SOCK_STREAM)

sock.connect(('localhost', 1200))

while True:
    data = sock.recv(1024)
    if not data:
        break

    doPrint = False
    needInput = False

    message = bytes()
    for b in [data[i:i+1] for i in range(len(data))]:
        if b == B_MESSAGE:
            doPrint = True
        if b == B_DONE:
            doPrint = False
        if b == B_INPUT:
            needInput = True
        if doPrint:
            message += b
    
    print(message.decode())
    if needInput:
        send_input('kys')


