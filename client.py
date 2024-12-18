import sys
import socket
import selectors
import types
import time
import os
import logging
import re
import struct

#Global Selector
sel = selectors.DefaultSelector()

#Global messages queued for sending
messages = []

#Global Client Gameboard
gameBoard = [[' ',' ',' '], [' ',' ',' '], [' ',' ',' ']]

#Glabal Game End Indicator
#Should be 1 or 0
gameEnd = 0

#Indicates what user 
isTurn = 0

#Global Socket Value
curSock = None

#Attempts a connection to server
#Registers sock and user input to selector
def start_connection(host, port):
    server_addr = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global curSock
    curSock = sock
    sock.settimeout(10)
    try:
        sock.connect(server_addr)
        logger.info(time.strftime("%a,%d-%b-%Y-%H:%M:%S", time.gmtime()) + ":Started connection to " + str(server_addr))
        print("Started connection to " + str(server_addr))
    except:
        logger.info(time.strftime("%a,%d-%b-%Y-%H:%M:%S", time.gmtime()) + ":This client was unable to connect to " + str(server_addr[0]) + str(server_addr[1]))
        print("This client was unable to connect to " + str(server_addr[0]) + str(server_addr[1]))
        exit()
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sockData = types.SimpleNamespace(
        type='sock',
        messages=list(messages),
        msg="This client is attempting to connect to the server",
        outb=b""
    )
    inputData = types.SimpleNamespace(
        type='input'
    )
    sel.register(sock, events, data=sockData)
    sel.register(sys.stdin, selectors.EVENT_READ, data=inputData)

#reads or writes data from server or user input
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        if data.type == 'input':
            service_user_input(sock)
        elif type(sock) is socket.socket:
            proccess_message(sock)
    if mask & selectors.EVENT_WRITE:
        if not data.outb and messages:
            data.outb = messages.pop(0)
        if data.outb:
            logger.info(time.strftime("%a,%d-%b-%Y-%H:%M:%S", time.gmtime()) + ":sending" + repr(data.outb) + "to connection to server")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

#Updates the Commandline UI after update
def update_UI(turnOrder):
    global isTurn
    print('_________________________________')
    print('Current  Format')
    print(' ' + gameBoard[0][0] + '|' + gameBoard[0][1] + '|' + gameBoard[0][2] + '   ' + '1|2|3')
    print(' ' + '-+-+-' + '   ' + '-+-+-')
    print(' ' +gameBoard[1][0] + '|' + gameBoard[1][1] + '|' + gameBoard[1][2] + '   ' + '4|5|6')
    print(' ' + '-+-+-' + '   ' + '-+-+-')
    print(' ' + gameBoard[2][0] + '|' + gameBoard[2][1] + '|' + gameBoard[2][2] + '   ' + '7|8|9')
    print('_________________________________')
    if isTurn == 0:
        print("It is opponents turn (B=Quit)")
    elif isTurn == 1:
        print("It is your turn, input 1-9 (1-9=Turn, B=Quit)")

def update_gameBoard(data):
    newdata = data.rsplit("[")
    #print(newdata)
    #able to do this cause it's small
    gameBoard[0][0] = newdata[1]
    gameBoard[0][1] = newdata[2]
    gameBoard[0][2] = newdata[3]
    gameBoard[1][0] = newdata[4]
    gameBoard[1][1] = newdata[5]
    gameBoard[1][2] = newdata[6]
    gameBoard[2][0] = newdata[7]
    gameBoard[2][1] = newdata[8]
    gameBoard[2][2] = newdata[9]

def proccess_message(sock):
    header = sock.recv(2)
    msg_len = int.from_bytes(header[0:2], byteorder="big")
    message = sock.recv(msg_len)
    decodedmess = message.decode('utf-8').rsplit(" - ")
    if decodedmess[0] == '1':
        print(decodedmess[1])
    elif decodedmess[0] == '2':
        global isTurn 
        isTurn = int(decodedmess[1])
        update_gameBoard(decodedmess[2])
        update_UI(str(decodedmess[1]))
    elif decodedmess[0] == '8':
        global gameEnd
        gameEnd = 1
        process_winner(decodedmess[1])

def process_winner(outcome):
    if outcome == '1':
        print('_________________________________')
        print('You have won!')
        print('_________________________________')
        print("Would you like to restart or quit? (A=Restart, B=Quit)")
    elif outcome == '0':
        print('_________________________________')
        print('Sorry, you have lost...')
        print('_________________________________')
        print("Would you like to restart or quit? (A=Restart, B=Quit)")
    elif outcome == 'DRAW':
        print('_________________________________')
        print('It is a draw!')
        print('_________________________________')
        print("Would you like to restart or quit? (A=Restart, B=Quit)")

#queues the turn made by user
def queue_turn(turn):
    encode = b"5 - " + turn.encode('utf-8')
    message = struct.pack(">H", len(encode)) + encode
    messages.append(message)

#queues a message saying user would like to restart game
#Should only available after the conclusion of a game
def queue_gameRestart():
    encode = b"6 - Game Restart"
    message = struct.pack(">H", len(encode)) + encode
    messages.append(message)

#Sends a disconnection message to server
#This does not queue message
#Allows server to free up resources for next user
def send_disconnection(sock):
    encode = b"9 - Disconnection"
    message = struct.pack(">H", len(encode)) + encode
    curSock.send(message)

#checks to see if the user has overwritten an already written space
def validInputCheck(turn):
    if turn == '1':
        if gameBoard[0][0] != ' ':
            return False
    elif turn == '2':
        if gameBoard[0][1] != ' ':
            return False
    elif turn == '3':
        if gameBoard[0][2] != ' ':
            return False
    elif turn == '4':
        if gameBoard[1][0] != ' ':
            return False
    elif turn == '5':
        if gameBoard[1][1] != ' ':
            return False
    elif turn == '6':
        if gameBoard[1][2] != ' ':
            return False
    elif turn == '7':
        if gameBoard[2][0] != ' ':
            return False
    elif turn == '8':
        if gameBoard[2][1] != ' ':
            return False
    elif turn == '9':
        if gameBoard[2][2] != ' ':
            return False
        
    return True

#Checks to see if user has made a proper input
def service_user_input(sock):
    line = sys.stdin.readline()
    global isTurn
    regEx = re.search("\A[1-9]\Z|\A[A-B]\Z", line[0])
    global gameEnd
    if len(line) <= 2 and regEx:
        if line[0] == 'A' and gameEnd == 1:
            print("Restarting Game")
            queue_gameRestart()
        elif line[0] == 'B':
            print("Closing connection") #close connection
            send_disconnection(sock)
            sel.close()
            curSock.close()
            #sel.unregister(sock)
            #sock.close()
            quit()
        else: #should probably check that 
            if isTurn == 1 and line[0] != 'A':
                if validInputCheck(line[0]):
                    print('User input: {}'.format(line)) 
                    queue_turn(line[0])
                else:
                    print("Invalid Input, choose a blank space")
            else:
                print('Wait for your opponent to take their turn...')
    else:
        print("Invalid Input") #should make this more descriptive

if not os.path.isdir('log'):
    os.mkdir('log')

#set up logger
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(levelname)s : %(message)s'
logFilename = "./log/client_TicTacToeLog(" + time.strftime("%a,%d-%b-%Y-%H:%M:%S", time.gmtime()) + ").log"
logging.basicConfig(filename=logFilename, level=logging.INFO, format=FORMAT)
print('Created ' + logFilename)

#Main function when running client script
def main():
    #checks correct arguments
    if len(sys.argv[1:]) != 4:
        print("Please run script with arguments for ip address and port")
        print("EX: python3 -i 0.0.0.0 -p 5022")
        exit()
    elif not ('-p' in sys.argv[1:]) or not ('-i' in sys.argv[1:]):
        print("Please run script with arguments for ip address and port")
        print("EX: python3 -i 0.0.0.0 -p 5022")
        exit()
    else:
        host = sys.argv[sys.argv[1:].index('-i') + 2]
        port = sys.argv[sys.argv[1:].index('-p') + 2]

    sys.stdout.flush()

    start_connection(host, int(port))

    #main loop
    try:
        while True:
            events = sel.select(timeout=1)
            if events:
                for key, mask in events:
                    service_connection(key, mask)
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        #approriatly 
        global curSock
        print("Caught keyboard interrupt, exiting")
        send_disconnection(curSock)
        print("Closing connection") #close connection
        sel.close()
        curSock.close()
    finally:
        sel.close()
        curSock.close()

#when script is run directly: call main
if __name__ == '__main__':
    main()