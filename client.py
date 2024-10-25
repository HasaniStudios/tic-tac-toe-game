import sys
import socket
import selectors
import types
import time
import os
import logging

sel = selectors.DefaultSelector()

messages = []

def start_connection(host, port, playerID):
    server_addr = (host, port)
    logger.info("Player" + playerID + "statered connection to" + str(server_addr))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect(server_addr)
    except:
        logger.info("This client was unable to connect to " + server_addr)
        exit()
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sockData = types.SimpleNamespace(
        type='sock',
        connid=playerID,
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
            for line in sys.stdin:
                print(line)
            #print('log: hello', file=sys.stdout)
            sys.stdout.flush()
        elif type(sock) is socket.socket:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                logger.info("received" + repr(recv_data) + "from connection")
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

def sendHeartBeat():
    #logger.info(
    Heartb= bytes(playerID, encoding="utf-8") + b" - Heart Beat "
    #logger(
    #sent = sock.send(Heartb)
    messages.append(Heartb)
    #selectors.EVENT_WRITE = True

def service_user_input():
    line = arg1.read()
    if line == 'quit\n':
        quit()
    else:
        print('User input: {}'.format(line))

port = input("What port are you trying to connect on? (Default:5022)")

host = input("What address are you trying to connect on? (Default: 0.0.0.0)")

playerID = input("What player number are you, 1 or 2?")

sys.stdout.flush()

#set up logger
logger = logging.getLogger(__name__)
os.remove('client_TicTacToe.log')
logging.basicConfig(filename='client_TicTacToe.log', level=logging.INFO)
print('Created client_TicTacToe.log')

print("Welcome to tick-tac-toe, would you like to (A=update, B=Quit)?")

start_connection(host, int(port), playerID)

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
            sendHeartBeat()
            curTime = time.perf_counter()
        if not sel.get_map():
            break

except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
