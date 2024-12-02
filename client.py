import sys
import socket
import selectors
import types
import time
import os
import logging
import re
import struct

sel = selectors.DefaultSelector()

messages = []
gameBoard = [[' ',' ',' '], [' ',' ',' '], [' ',' ',' ']]
gameEnd = 0

isTurn = 0

curSock = None

#recv_data = ''

def start_connection(host, port):
    server_addr = (host, port)
    #logger.info("Started connection to" + str(server_addr))
    #print("Started connection to" + str(server_addr))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global curSock
    curSock = sock
    sock.settimeout(10)
    try:
        sock.connect(server_addr)
        logger.info("Started connection to " + str(server_addr))
        print("Started connection to " + str(server_addr))
    except:
        logger.info("This client was unable to connect to " + str(server_addr[0]) + str(server_addr[1]))
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

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        if data.type == 'input':
            service_user_input(sock)
            #print('log: hello', file=sys.stdout)
            sys.stdout.flush()
        elif type(sock) is socket.socket:
            proccess_message(sock)
            #recv_data = sock.recv(1024)  Should be ready to read
            #if recv_data:
                #proccess_message(recv_data)
                #logger.info("received" + repr(recv_data) + "from connection")
                #print("received" + repr(recv_data) + "from connection")
                #pretty sure I don't need this line
	        #data.recv_total += len(recv_data)
        '''
        if not recv_data or data.recv_total >= data.msg_total:
            print("closing connection", data.connid)
            sel.unregister(sock)
            sock.close()
        '''
    if mask & selectors.EVENT_WRITE:
        if not data.outb and messages:
            data.outb = messages.pop(0)
        if data.outb:
            logger.info("sending" + repr(data.outb) + "to connection to server")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

host = '127.0.0.1'  #using local address since I am unsure how this is being run
host = '0.0.0.0'
port = 5022
#num_conns = 10

#4 types of message will be sent by client including
# - HeartBeat: 1
# - Connection: 2
# - Update: 3
# - Disconnection: 4

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
    #print(decodedmess)
    if decodedmess[0] == '0':
        #print("heart beat recived")
        pass
    elif decodedmess[0] == '1':
        print(decodedmess[1])
    elif decodedmess[0] == '2':
        global isTurn 
        isTurn = int(decodedmess[1])
        #print(isTurn)
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

def sendHeartBeat():
    #logger.info(
    Heartb= b"0 - Heart Beat"
    #logger(
    #sent = sock.send(Heartb)
    messages.append(Heartb)
    #selectors.EVENT_WRITE = True

def queue_turn(turn):
    encode = b"5 - " + turn.encode('utf-8')
    message = struct.pack(">H", len(encode)) + encode
    messages.append(message)

def queue_gameRestart():
    encode = b"6 - Game Restart"
    message = struct.pack(">H", len(encode)) + encode
    messages.append(message)

def send_disconnection(sock):
    encode = b"9 - Disconnection"
    message = struct.pack(">H", len(encode)) + encode
    curSock.send(message)

def service_user_input(sock):
    line = sys.stdin.readline()
    global isTurn
    #print(line)
    #print(len(line))
    regEx = re.search("\A[1-9]\Z|\A[A-B]\Z", line[0])
    #print(re.search)
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
                print('User input: {}'.format(line))
                queue_turn(line[0])
            else:
                print('Wait for your opponent to take their turn...')
    else:
        print("Invalid Input") #should make this more descriptive

#set up logger
logger = logging.getLogger(__name__)
os.remove('client_TicTacToe.log')
logging.basicConfig(filename='client_TicTacToe.log', level=logging.INFO)
print('Created client_TicTacToe.log')

def main():

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

    #port = input("What port are you trying to connect on? (Default:5022)")

    #host = input("What address are you trying to connect on? (Default: 0.0.0.0)")

    #playerID = input("What player number are you, 1 or 2?")

    sys.stdout.flush()

    #print("Welcome to tick-tac-toe")

    start_connection(host, int(port))

    #main loop
    try:
        curTime = time.perf_counter()
        updTime = time.perf_counter()
        #print(time.perf_counter())
        updateServer = False
        while True:
            #print(time.perf_counter())
            events = sel.select(timeout=1)
            if events:
                for key, mask in events:
                    service_connection(key, mask)
                updateServer = False
            if time.perf_counter() - curTime >= 2:
                #Heart beat system is most likely not needed rn
                #sendHeartBeat()
                curTime = time.perf_counter()
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        global curSock
        send_disconnection(curSock)
        print("caught keyboard interrupt, exiting")
        print("Closing connection") #close connection
        sel.close()
        curSock.close()
    finally:
        sel.close()
        curSock.close()

#when script is run directly: call main
if __name__ == '__main__':
    main()