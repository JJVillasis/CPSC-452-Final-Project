import selectors
import socket
import sys
import types

sel = selectors.DefaultSelector()

#Creates new socket and adds it to selector
def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr = addr, inb = b"", outb = b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data = data)

#Handles client connections
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    #Socket is ready to read Client's data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        #Data received from Client
        if recv_data:
            data.outb += recv_data
        #No data received from Client
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    #Echo received data back to Client
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

#Check if user entered correct amount of commands
if len(sys.argv) != 3:
    print("ERROR: User must specify <HOST ADDRESS> and <PORT NUMBER>.")
    print()
    exit(-1)

#Get host address, and port number
host, port = sys.argv[1], int(sys.argv[2])

#TESTING - Print entered host and port
print("Host address:", host)
print("Port number:", port)
print()

#Create listening socket
hostSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostSock.bind((host, port))
hostSock.listen()
print(f"Listening on {(host, port)}")
hostSock.setblocking(False)
sel.register(hostSock, selectors.EVENT_READ, data=None)

#Host Server Event Loop
try:
    while True:
        events = sel.select(timeout = None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)

                if key.data.outb:
                    print(f"Testing: {key.data.outb}")
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()