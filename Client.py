import socket
import sys
from time import sleep

#Parse command line to get <HOST> and <PORT>
if len(sys.argv) != 3:
    print("ERROR: User must specify <HOST ADDRESS> and <PORT>.\n")
    exit(-1)

#The remote host
HOST, PORT = sys.argv[1], int(sys.argv[2])

print(f"Connecting to {(HOST, PORT)}...\n")
sleep(2)

#Establish client Socket
cliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect to host server
cliSock.connect((HOST, PORT))

print("Connection successful!\n")

#################### Client Functions ####################

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

#################### Client Login ####################

#Login to server
print("LOG INTO YOUR ACCOUNT:")
username = input("Username: ")
sendMsg(cliSock, username)
password = input("Password: ")
sendMsg(cliSock, password)

print("\nVerifying account...")

#Verify account
if recvMsg(cliSock).decode() == "FALSE":
    print("ERROR: <USERNAME> or <PASSWORD> not found.\n")
    exit(-1)

#Check if account is logged in to another socket
if recvMsg(cliSock).decode() == "FALSE":
    print("ERROR: Account logged in to another socket.\n")
    exit(-1)

#Server Hello
print("\nAccount Found!\n")
hello = recvMsg(cliSock)
print(hello.decode())

#################### Client Event Loop ####################

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

    print(f"Received: {data.decode()}\n")