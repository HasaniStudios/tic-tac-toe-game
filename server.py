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
        queue_announcment(conn, "You are considered player X.")
        queue_announcment(conn, "Waiting for second player...")
    elif len(playerSock) == 2:
        queue_announcment(conn, "You are considered player O.")
        queue_announcment(playerSock[0], "Second player has connected.")
        global turnOrder
        turnOrder = random.randint(1, 2)
        print(turnOrder)
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
        process_message(sock)
        #recv_data = sock.recv(1024)
        #if recv_data:
        #messages.append((sock, recv_data))
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

def wipeGameBoard():
    global gameBoard
    for x in range(3):
        for y in range(3):
            gameBoard[x][y] = ' '

def process_message(sock):
    header = sock.recv(2)
    msg_len = int.from_bytes(header[0:2], byteorder="big")
    message = sock.recv(msg_len)
    decodedmess = message.decode('utf-8').rsplit(" - ")
    #print(decodedmess)
    if decodedmess[0] == '5':
        process_turnOrder(decodedmess[1], sock)
    elif decodedmess[0] == '6':
        wipeGameBoard()
        global turnOrder
        turnOrder = random.randint(1, 2)
        #print(turnOrder)
        if sock == playerSock[0]:
            queue_announcment(playerSock[1], "Opponent restarted game")
        if sock == playerSock[1]:  
            queue_announcment(playerSock[0], "Opponent restarted game")
        print("test: " + str(turnOrder))
        if turnOrder == 1:
            queue_update(playerSock[0], "1")
            queue_update(playerSock[1], "0")
        if turnOrder == 2:  
            queue_update(playerSock[0], "0")
            queue_update(playerSock[1], "1")
    elif decodedmess[0] == '9':
        print('hello')
        if sock == playerSock[0]:
            queue_announcment(playerSock[1], "Opponent disconnected from game")
            queue_announcment(playerSock[1], "You are considered player X.")
            queue_announcment(playerSock[1], "Waiting for second player...")
            wipeGameBoard()
            sel.unregister(playerSock[0])
            playerSock[0].close()
            playerSock.pop(0)
            print(playerSock)
        if sock == playerSock[1]:  
            queue_announcment(playerSock[0], "Opponent disconnected from game")
            queue_announcment(playerSock[0], "You are considered player X.")
            queue_announcment(playerSock[0], "Waiting for second player...")
            wipeGameBoard()
            sel.unregister(playerSock[1])
            playerSock[1].close()
            playerSock.pop(1)
            print(playerSock)
        
def update_serverside_board(turnNumber, character):
    global gameBoard
    if int(turnNumber) <= 3:
        gameBoard[0][int(turnNumber)-1] = character
    elif int(turnNumber) <= 6:
        gameBoard[1][int(turnNumber)-4] = character
    elif int(turnNumber) <= 9:
        gameBoard[2][int(turnNumber)-7] = character
    else:
        print("Error: Bad turnNumber")

def win_condtion():
    global gameBoard
    increment = 0
    character = ' '

    if gameBoard[0][0] == 'X' or gameBoard[0][0] == 'O':
        character = gameBoard[0][0]
        if gameBoard[0][1] == character and gameBoard[0][2] == character:
            return character
        elif gameBoard[1][1] == character and gameBoard[2][2] == character:
            return character
        elif gameBoard[1][0] == character and gameBoard[2][0] == character:
            return character
        
    if gameBoard[2][2] == 'X' or gameBoard[2][2] == 'O':
        character = gameBoard[2][2]
        if gameBoard[1][2] == character and gameBoard[0][2] == character:
            return character
        elif gameBoard[2][1] == character and gameBoard[2][0] == character:
            return character
    
    if gameBoard[1][1] == 'X' or gameBoard[1][1] == 'O':
        character = gameBoard[1][1]
        if gameBoard[0][1] == character and gameBoard[2][1] == character:
            return character
        elif gameBoard[1][0] == character and gameBoard[1][2] == character:
            return character
        elif gameBoard[0][2] == character and gameBoard[2][0] == character:
            return character
        
    return ' '
    #Attempt at making a complex algorithm to check for winning condition
    '''
    for x in range(3):
        for y in range(3):
            if gameBoard[x][y] == 'X' or gameBoard[x][y] == 'O':
                    increment +=1
                    character = gameBoard[x][y]
                    for a in range(x, x+2):
                        for b in range(y+1, y+2):
    '''

def queue_winner(winner):
    global playerSock
    encode1 = b"8 - 1"
    message1 = struct.pack(">H", len(encode1)) + encode1
    encode2 = b"8 - 0"
    message2 = struct.pack(">H", len(encode2)) + encode2
    if winner == 'X':
        messages.append((playerSock[0], message1))
        messages.append((playerSock[1], message2))
    elif winner == 'O':
        messages.append((playerSock[1], message1))
        messages.append((playerSock[0], message2))

def process_turnOrder(turnNumber, socket):
    global turnOrder
    global playerSock
    if turnOrder == 1:
        update_serverside_board(turnNumber, 'X')
        winner = win_condtion()
        if winner == ' ':
            queue_update(playerSock[0], "0")
            queue_update(playerSock[1], "1")
            turnOrder = 2
        else:
            queue_winner(winner)
    elif turnOrder == 2:
        update_serverside_board(turnNumber, 'O')
        winner = win_condtion()
        if winner == ' ':
            queue_update(playerSock[0], "1")
            queue_update(playerSock[1], "0")
            turnOrder = 1
        else:
            queue_winner(winner)

#need to make this take in arguments
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
