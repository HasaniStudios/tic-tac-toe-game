import sys
import socket
import selectors
import types
import time

sel = selectors.DefaultSelector()

messages = [b"Update Server", b"Update Server", b"Update Server" b"Update Server"]

def start_connection(host, port, num_conns, playerID):
    server_addr = (host, port)
    print("Player", playerID, "statered connection to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect(server_addr)
    except:
        print("This client was unable to connect to ", server_addr)
        exit()
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
        #msg_total=sum(len(m) for m in messages),
        msg_total=300,
        recv_total=0,
        connid=playerID,
        messages=list(messages),
        msg="This client is attempting to connect to the server",
        outb=b""
    )
    sel.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total >= data.msg_total:
            print("closing connection", data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("sending", repr(data.outb), "to connection to server")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

host = '127.0.0.1'  #using local address since I am unsure how this is being run
port = 5022
num_conns = 10       

def sendHeartBeat(key):
    sock = key.fileobj
    print("Player", playerID, "is sending heart beat message to server")
    Heartb= bytes(playerID, encoding="utf-8") + b" - Heart Beat "
    sent = sock.send(Heartb)

playerID = input("What player number are you, 1 or 2?")

start_connection(host, port, num_conns, playerID)

try:
    curTime = time.perf_counter()
    updTime = time.perf_counter()
    #print(time.perf_counter())
    updateServer = False
    while True:
        #print(time.perf_counter())
        events = sel.select(timeout=1)
        if updateServer:
            for key, mask in events:
                service_connection(key, mask)
            updateServer = False
        if time.perf_counter() - curTime >= 2:
            for key, mask in events:
                sendHeartBeat(key)
            curTime = time.perf_counter()
        if not sel.get_map():
            break
        if time.perf_counter() - updTime >= 5:
            updateServer = True
            updTime = time.perf_counter()

except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()