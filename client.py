import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

messages = [b"Message 1 from client.", b"Message 2 from client."]

def start_connection(host, port, num_conns):
    connid = 1
    server_addr = (host, port)
    print("starting connection", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect(server_addr)
    except:
        print("This client was unable to connect to ", server_addr)
        exit()
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
        msg_total=sum(len(m) for m in messages),
        recv_total=0,
        connid=1,
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
        print(recv_data)
        print(data.recv_total)
        print(data.msg_total)
        if recv_data:
            print("received", repr(recv_data), "from connection")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
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
port = 5050
num_conns = 10       

start_connection(host, port, num_conns)

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()