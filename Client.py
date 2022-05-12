import socket

HOST = '127.0.0.1'    # The remote host
PORT = 57000              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #Connect to Host
    sock.connect((HOST, PORT))

    #Event Loop
    while True:
        userInput = input("Send Something to the Host: ")
        sock.sendall(userInput.encode("utf-8"))
        data = sock.recv(1024)

        if data.decode("utf-8").lower() == "goodbye":
            print(f"Connection ended with {HOST}. Goodbye")
            break

        if data:
            dataD = data.decode("utf-8")
            print('Received:', dataD)