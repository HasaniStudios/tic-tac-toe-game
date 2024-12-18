import sys
import socket
import selectors
import types
import json
import struct
import random
import time
import logging
import os

sel = selectors.DefaultSelector()
playerSock = []

#using similar messaging system as client
messages = []

turnOrder = 0

gameBoard = [[' ',' ',' '], [' ',' ',' '], [' ',' ',' ']]

#accepts incoming connection requests
def accept_wrapper(sock):
    conn, addr = sock.accept()
    conn.settimeout(10)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    playerSock.append(conn)
    if len(playerSock) == 1:
        print("accepted connection from", addr, "this user will be considered player X")
        logger.info("accepted connection from" + str(addr) + "this user will be considered player X")
        queue_announcment(conn, "You are considered player X.")
        queue_announcment(conn, "Waiting for second player...")
    elif len(playerSock) == 2:
        print("accepted connection from", addr, "this user will be considered player O")
        logger.info("accepted connection from" + str(addr) + "this user will be considered player O")
        queue_announcment(conn, "You are considered player O.")
        queue_announcment(playerSock[0], "Second player has connected.")
        global turnOrder
        turnOrder = random.randint(1, 2)
        if turnOrder == 1:
            queue_update(playerSock[0], "1")
            queue_update(playerSock[1], "0")
        if turnOrder == 2:  
            queue_update(playerSock[0], "0")
            queue_update(playerSock[1], "1")

#services connection by either reading or writing data from clients
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        process_message(sock)
    if mask & selectors.EVENT_WRITE:
        if not data.outb and messages:
            data.outb = messages.pop(0)
        if data.outb:
            logger.info("sent" + str(repr(data.outb[1])) + "to" + str(data.addr))
            #print("sent", repr(data.outb[1]), "to", data.addr)
            sent = data.outb[0].send(data.outb[1])  # Should be ready to write
            data.outb = ''

#queues an announcment to given client
def queue_announcment(sock, text):
    encode = b"1 - " + text.encode('utf-8')
    message = struct.pack(">H", len(encode)) + encode
    messages.append((sock, message))

#Updates client Board with new data
def queue_update(sock, turn):
    encode = b"2 - " + turn.encode('utf-8') + b" - "
    gameBoardData = '[' + str(gameBoard[0][0]) + '[' + str(gameBoard[0][1]) + '[' + str(gameBoard[0][2])
    gameBoardData += '[' + str(gameBoard[1][0]) + '[' + str(gameBoard[1][1]) + '[' + str(gameBoard[1][2])
    gameBoardData += '[' + str(gameBoard[2][0]) + '[' + str(gameBoard[2][1]) + '[' + str(gameBoard[2][2])
    encode += gameBoardData.encode('utf-8')
    message = struct.pack(">H", len(encode)) + encode
    messages.append((sock, message))

#wipes serverside board for next game
def wipeGameBoard():
    global gameBoard
    for x in range(3):
        for y in range(3):
            gameBoard[x][y] = ' '

#process different messages recieved by the clients
def process_message(sock):
    header = sock.recv(2)
    msg_len = int.from_bytes(header[0:2], byteorder="big")
    message = sock.recv(msg_len)
    decodedmess = message.decode('utf-8').rsplit(" - ")
    if decodedmess[0] == '5':
        process_turnOrder(decodedmess[1], sock)
    elif decodedmess[0] == '6':
        wipeGameBoard()
        global turnOrder
        turnOrder = random.randint(1, 2)
        if sock == playerSock[0]:
            queue_announcment(playerSock[1], "Opponent restarted game")
        if sock == playerSock[1]:  
            queue_announcment(playerSock[0], "Opponent restarted game")
        if turnOrder == 1:
            queue_update(playerSock[0], "1")
            queue_update(playerSock[1], "0")
        if turnOrder == 2:  
            queue_update(playerSock[0], "0")
            queue_update(playerSock[1], "1")
    elif decodedmess[0] == '9':
        if sock == playerSock[0]:
            #need to test this
            print("player X has disconnected from the game")
            logger.info("player X has disconnected from the game")
            if len(playerSock) == 2:
                queue_announcment(playerSock[1], "Opponent disconnected from game")
                queue_announcment(playerSock[1], "You are considered player X.")
                queue_announcment(playerSock[1], "Waiting for second player...")
            wipeGameBoard()
            sel.unregister(playerSock[0])
            playerSock[0].close()
            playerSock.pop(0)
        elif sock == playerSock[1]:
            print("player O has disconnected from the game")
            logger.info("player O has disconnected from the game")  
            queue_announcment(playerSock[0], "Opponent disconnected from game")
            queue_announcment(playerSock[0], "You are considered player X.")
            queue_announcment(playerSock[0], "Waiting for second player...")
            wipeGameBoard()
            sel.unregister(playerSock[1])
            playerSock[1].close()
            playerSock.pop(1)
        
#updates the serverside board with the proper character
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
        logger.error("Error: Bad value for a potential turn detected")
        quit()

#check to see if the board has reached a win condition
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

    #Counts number of empty spaces
    emptyNumber = 0    
    for i in range(len(gameBoard)):
        for j in range(len(gameBoard[i])):
            if (gameBoard[i][j] == ' '):
                emptyNumber += 1

    #checks to see if all nine spaces have been filled
    #allows checing for a draw
    if emptyNumber == 0:
        return '-'
    else:
        return ' '

#Queues winner message
def queue_winner(winner):
    global playerSock
    encode1 = b"8 - 1"
    message1 = struct.pack(">H", len(encode1)) + encode1
    encode2 = b"8 - 0"
    message2 = struct.pack(">H", len(encode2)) + encode2
    if winner == 'X':
        #if the win condition is calculated as an X win
        messages.append((playerSock[0], message1))
        messages.append((playerSock[1], message2))
    elif winner == 'O':
        #if the win condition is calculated as a O win
        messages.append((playerSock[1], message1))
        messages.append((playerSock[0], message2))
    elif winner == '-':
        #if the win condition is calculated as a draw
        encode3 = b"8 - DRAW"
        message3 = struct.pack(">H", len(encode3)) + encode3
        messages.append((playerSock[0], message3))
        messages.append((playerSock[1], message3))

#Proccess turn taken, sees if a win condition has been met, and and sends updates to client
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

if not os.path.isdir('log'):
    os.mkdir('log')

logger = logging.getLogger(__name__)
logFilename = "./log/server_TicTacToeLog(" + time.strftime("%a,%d-%b-%Y-%H:%M:%S", time.gmtime()) + ").log"
FORMAT = '%(asctime)s - %(levelname)s : %(message)s'
logging.basicConfig(filename=logFilename, level=logging.INFO,  format=FORMAT)
print('Created ' + logFilename)

#Main function when running server script
def main():
    #Default arguments
    host = '0.0.0.0'
    port = 5023

    if len(sys.argv[1:]) != 2:
        print("Please run script with arguments for port")
        print("EX: python3 server.py -p 5022")
        exit()
    elif not ('-p' in sys.argv[1:]):
        print("Please run script with arguments for port")
        print("EX: python3 server.py -p 5022")
        exit()
    else:
        port = sys.argv[sys.argv[1:].index('-p') + 2]

    #creates socket and register
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, int(port)))
    lsock.listen()
    print("This server is listening for players to connect on host:", host, "and Port:", port)
    lsock.settimeout(10)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    #main loop
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
        sel.close()
        lsock.close()
        #release logger resources
        handlers = logger.handlers[:]
        for handler in handlers:
            logger.removeHandler(handler)
            handler.close()
    finally:
        sel.close()
        lsock.close()
        #release logger resources
        handlers = logger.handlers[:]
        for handler in handlers:
            logger.removeHandler(handler)
            handler.close()

#when script is run directly: call main
if __name__ == '__main__':
    main()