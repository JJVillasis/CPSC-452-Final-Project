import socket

HOST = '127.0.0.1'    # The remote host
PORT = 1234              # The same port as used by the server

#TESTING - Print entered host and port
print("Host address:", HOST)
print("Port number:", PORT)
print()

#Establish client Socket
cliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect to host server
cliSock.connect((HOST, PORT))

################################################
# recvMsg - The function to handle the message #
#             of the specified format          #
# @param sock - socket to receive message      #
# @returns the message without the header      #
################################################
def recvMsg(sock):
    
    # The size
    size = sock.recv(3)
    
    # Convert the size to the integer
    intSize = int(size)

    # Receive the data
    data = sock.recv(intSize)

    return data

#################################################
# sendMSG - Format given message and send it to #
#             the host server.                  #
# @param sock - The socket to the message.      #
# @param msg - The message to be sent.          #
#################################################
def sendMsg(sock, msg):

    #Get length of the message
    msgLen = str(len(msg))

    #Prepend header "000" to message
    while len(msgLen) < 3:
        msgLen = "0" + msgLen

    #Encode the message header into a byte array
    msgLen = msgLen.encode()

    #Combine message with header
    msgSend = msgLen + msg.encode()

    #Send message to host
    sock.sendall(msgSend)

#Send Username to Host
username = input("Username: ")
sendMsg(cliSock, username)


#Event Loop
while True:
    #Send message to the host
    userInput = input("Send Something to the Host: ")
    sendMsg(cliSock, userInput)

    #Wait for responce from host
    data = recvMsg(cliSock)

    #End connection with host
    if data.decode() == "goodbye":
        print(f"Connection ended with {HOST}. Goodbye.")
        break

    dataD = data.decode()
    print('Received:', dataD)