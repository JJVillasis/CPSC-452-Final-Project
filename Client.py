from Crypto.Hash import SHA256
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from getpass import getpass
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

def sendSign(sock, sign):

    #Get length of the message
    signLen = str(len(sign))

    #Prepend header "000" to message
    while len(signLen) < 3:
        signLen = "0" + signLen

    #Encode the message header into a byte array
    signLen = signLen.encode()

    #Combine message with header
    signSend = signLen + sign

    #Send message to host
    sock.sendall(signSend)

##################################################################
# signDSA - Use DSA to sign a message.                           #
# @param message - The message to be signed.                     #
# @param keyFile - The file name of the PEM that stores the key. #
# @param password - Password to the key (if used).               #
# @returns signature associated with the message.                #
##################################################################

def signDSA(message, keyFile, password):

    #Retrieve private key
    with open("Private Key PEMs/" + keyFile, "rb") as file:
        if password.lower() == "none":
            PR = DSA.importKey(file.read())
        elif password:
            PR = DSA.importKey(file.read(), password)

    #Create hash of message
    hashedMessage = SHA256.new(message.encode())
    signer = DSS.new(PR, "fips-186-3")

    #Sign the message
    signature = signer.sign(hashedMessage)

    return signature


#################### Account Login ####################

#Login to server
print("==============================")
print("LOG INTO YOUR ACCOUNT:")
username = input("Username: ")
sendMsg(cliSock, username)
sendMsg(cliSock, getpass("Password: "))

print("\nVerifying account...")

#Verify account
if recvMsg(cliSock).decode() == "False":
    print("ERROR: <USERNAME> or <PASSWORD> not found.\n")
    exit(-1)

#Check if account is logged in to another socket
if recvMsg(cliSock).decode() == "False":
    print("ERROR: Account logged in to another socket.\n")
    exit(-1)

#Server Hello
print("Account Found!")
print("==============================\n")
print(recvMsg(cliSock).decode())


#################### Client Event Loop ####################

while True:
    # #Send message to the host
    # userInput = input("Send Something to the Host: ")
    # sendMsg(cliSock, userInput)

    # #Wait for response from host
    # data = recvMsg(cliSock)

    # #End connection with host
    # if data.decode() == "goodbye":
    #     print(f"Connection ended with {HOST}. Goodbye.")
    #     break

    # print(f"Received: {data.decode()}\n")

    ########## DSA Verification ##########

    #Get type and message
    message = input("Send something to the Host: ")
    dsType = input("Digital Signature type (DSA/RSA): ")

    #Sign message
    signature = signDSA(message, "private" + username + dsType.upper() + ".pem", getpass("Enter keypass (\'None\' if no password): "))

    #Send type, message, and signature to Server
    sendMsg(cliSock, dsType)
    sendMsg(cliSock, message)
    sendSign(cliSock, signature)

    #Check if message is verified
    if recvMsg(cliSock).decode() == "True":
        print("Message verified.")

        data = recvMsg(cliSock)

        #End connection with host
        if data.decode() == "goodbye":
            print(f"Connection ended with {HOST}. Goodbye.")
            break

        print(f"Received: {data.decode()}\n")

    else:
        print("Message invalidated.")
        break

