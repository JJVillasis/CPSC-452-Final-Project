import socket

HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((HOST, PORT))
	userInput = input("Send Something to the Host: ")
	s.sendall(userInput.encode("utf-8"))
	data = s.recv(1024)

	if data:
	    dataD = data.decode("utf-8")
	    print('Received:', dataD)