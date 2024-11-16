import sys
import socket
import selectors
import types
import json
import struct
import random

sel = selectors.DefaultSelector()
playerSock = []

#using similar messaging system as client
messages = []

turnOrder = 0

gameBoard = [[' ',' ',' '], [' ',' ',' '], [' ',' ',' ']]

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print("accepted connection from", addr, "this user will be considered player 1")
    conn.settimeout(10)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    playerSock.append(conn)
    if len(playerSock) == 1:
        queue_announcment(conn, "You are considered player 1.")
        queue_announcment(conn, "Waiting for second player...")
    elif len(playerSock) == 2:
        queue_announcment(conn, "You are considered player 2.")
        queue_announcment(playerSock[0], "Second player has connected.")
        turnOrder = random.randint(1, 2)
        print("test: " + str(turnOrder))
        if turnOrder == 1:
            queue_update(playerSock[0], "1")
            queue_update(playerSock[1], "0")
        if turnOrder == 2:  
            queue_update(playerSock[0], "0")
            queue_update(playerSock[1], "1")

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            messages.append((sock, recv_data))
            #data.outb = recv_data
        #else:
        #    print("closing connection to", data.addr)
        #    sel.unregister(sock)
        #    sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and messages:
            data.outb = messages.pop(0)
        if data.outb:
            print("echoing", repr(data.outb[1]), "to", data.addr)
            sent = data.outb[0].send(data.outb[1])  # Should be ready to write
            data.outb = ''

#queues an announcment to given  
def queue_announcment(sock, text):
    encode = b"1 - " + text.encode('utf-8')
    message = struct.pack(">H", len(encode)) + encode
    messages.append((sock, message))

def queue_update(sock, turn):
    encode = b"2 - " + turn.encode('utf-8') + b" - "
    gameBoardData = '[' + str(gameBoard[0][0]) + '[' + str(gameBoard[0][1]) + '[' + str(gameBoard[0][2])
    gameBoardData += '[' + str(gameBoard[1][0]) + '[' + str(gameBoard[1][1]) + '[' + str(gameBoard[1][2])
    gameBoardData += '[' + str(gameBoard[2][0]) + '[' + str(gameBoard[2][1]) + '[' + str(gameBoard[2][2])
    encode += gameBoardData.encode('utf-8')
    message = struct.pack(">H", len(encode)) + encode
    messages.append((sock, message))

host = '0.0.0.0'
port = 5023

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("This server is listening for players to connect", (host, port))
lsock.settimeout(10)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
