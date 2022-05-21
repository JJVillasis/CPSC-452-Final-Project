from Crypto.Hash import SHA256
from Crypto.PublicKey import DSA, RSA
from Crypto.Signature import DSS, pkcs1_15
import json
import socket
import sys
import threading
from time import sleep

#################### Server Initialization ####################

#Parse command line to get <HOST> and <PORT>
if len(sys.argv) == 2:
    #The remote host and port
    HOST = ""

    #Check if argument is <PORT>
    try:
        eval(sys.argv[1])
    except SyntaxError:
        print("ERROR: User must specify <PORT>. Optionally, also specify <HOST ADDRESS>.\n")
        exit(-1)

    PORT = int(sys.argv[1])

elif len(sys.argv) == 3:
    #Check if arguments are in the correct order
    try:
        eval(sys.argv[2])
    except SyntaxError:
        print("ERROR: User must specify arguments in the correct order: <HOST ADDRESS> <PORT>\n")
        exit(-1)

    HOST, PORT = sys.argv[1], int(sys.argv[2])

else:
    print("ERROR: User must at least specify <PORT>. Optionally, also specify <HOST ADDRESS>.\n")
    exit(-1)

#The socket the server uses for listening
listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind socket to specified
listenSock.bind((HOST, PORT))

print(f"Listening on {(HOST, PORT)}.\n")

#Start listening with a connection backlog queue of 100
listenSock.listen(100)

#The user name to socket dictionary
usernameToSockDic = {}


#################### Server Functions ####################

########################################################
# getID - find if username is found in account records #
# @param username - the name to search for             #
# @returns account if found, or False is not           #
########################################################
def getID(username):
    
    #Open and parse Accounts.json
    file = open("Accounts.json")
    accounts = json.load(file)

    #Search for account
    for x in accounts["Accounts"]:
        if x["username"] == username:
            return x

    return False

########################################################
# verifyAccount - verifies that the specified username #
#                 and password is found in accounts    #
# @param username - the name to search for             #
# @param password - the password associated with user  #
# @returns if account was found                        #
########################################################
def verifyAccount(username, password):
    
    #Check username
    account = getID(username)
    
    #Check if account exists
    if account:
        
        #Find sha256 hash of password
        hashedPass = SHA256.new(password.encode())
        hexDig = hashedPass.hexdigest()

        #Check if password is found
        if hexDig == account["password"]:
            return account
    
    return False

######################################################
# sendMsg - Puts the message into the formatted form #
#           and sends it over the socket             #
# @param sock - the socket to send the message       #
# @param msg - the message                           #
######################################################
def sendMsg(sock, msg):

    #Get the message length
    msgLen = str(len(msg))
    
    #Keep prepending 0's until we get a header of 3 
    while len(msgLen) < 3:
        msgLen = "0" + msgLen
    
    #Encode the message into bytes
    msgLen = msgLen.encode()
    
    #Put together a message
    sMsg = msgLen + msg.encode()
    
    #Send the message
    sock.sendall(sMsg)



##############################################################
# The function to handle the message of the specified format #
# @param sock - the socket to receive the message from       #
# @returns the message without the header                    #
##############################################################
def recvMsg(sock):
    
    #The size
    size = sock.recv(3)
    
    #Convert the size to the integer
    intSize = int(size)

    #Receive the data
    data = sock.recv(intSize)

    return data


##################################################################
# verifyDSA - Use DSA to verify a message with a signature.      #
# @param message - The message to be signed.                     #
# @param signature - Possible signature associated with message. #
# @param keyFile - The file name of the PEM that stores the key. #
# @returns if verification succeed.                              #
##################################################################
def verifyDSA(message, signature, keyFile):

    #Retrieve public key
    with open("Public Key PEMs/" + keyFile, "rb") as file:
        PU = DSA.importKey(file.read())

    #Create hash of message
    hashedMessage = SHA256.new(message)
    verifier = DSS.new(PU, "fips-186-3")

    #Attempt verification
    try:
        verifier.verify(hashedMessage, signature)
        return True
    except ValueError:
        return False

##################################################################
# verifyRSA - Use RSA to verify a message with a signature.      #
# @param message - The message to be signed.                     #
# @param signature - Possible signature associated with message. #
# @param keyFile - The file name of the PEM that stores the key. #
# @returns if verification succeed.                              #
##################################################################
def verifyRSA(message, signature, keyFile):
    
    #Retrieve public key
    with open("Public Key PEMs/" + keyFile, "rb") as file:
        PU = RSA.import_key(file.read())

    #Get message hash
    hashedMessage = SHA256.new(message)

    #Attempt Verification
    try:
        pkcs1_15.new(PU).verify(hashedMessage, signature)
        return True
    except (ValueError, TypeError):
        return False

####################################################################
# verifyMessage - Verify the signature of a message using RSA/DSA. #
# @param signType - The digital signature scheme to be used.       #
# @param message - The message to be signed.                       #
# @param signature - Possible signature associated with message.   #
# @param account - account of the client                           #
# @returns if verification succeed.                                #
####################################################################
def verifyMessage(signType, message, signature, account):

    #DSA Signature Verification
    if signType.upper() == "DSA":
        return verifyDSA(message, signature, account["publicDSA"])

    #RSA Signature Verification
    elif signType.upper() == "RSA":
        return verifyRSA(message, signature, account["publicRSA"])

    #Unknown Scheme
    else:
        return False


#############################################################################
# serviceClient - Will be called by the thread that handles a single client #
# @param clisock - the client socket                                        #
# @param username - the user name to serve                                  #
#############################################################################
def serviceClient(cliSock, account):

    # Keep servicing the client until it disconnects
    while cliSock:

        #Get signature type, message, and signature
        signType = recvMsg(cliSock)
        message = recvMsg(cliSock)
        signature = recvMsg(cliSock)

        #Verify message
        sleep(1)
        if verifyMessage(signType.decode(), message, signature, account):

            #Message signature verified
            print(f"Message {message} verified")
            sendMsg(cliSock, "True")

            #Print retreived message
            print(f"Got data {message} from client socket {cliSock.getpeername()}\n")

            #Check if client ended connection
            if message.decode() == "goodbye":
                sendMsg(cliSock, message.decode()) 
                break

            #Echo message to client
            sendMsg(cliSock, "Echo: " + message.decode())

        else:
            #Message signature rejected
            print("Message invalidated")
            sendMsg(cliSock, "False")
            break

    #Connection ended with client
    print(f"Ending connection with {cliSock.getpeername()}\n")

    #Remove Socket from dictionary
    del usernameToSockDic[account["username"]]


#################### Server Loop ####################

while True:
    
    #Accept the connection
    clienComSock, cliInfo = listenSock.accept()

    print(f"New client connected: {cliInfo}")
    
    #Get the username and password
    #Check if account exists in account records
    account = verifyAccount(recvMsg(clienComSock).decode(), recvMsg(clienComSock).decode())

    sleep(1)
    if account:
        
        #send that account is found
        print("\nAccount verified.\n")
        sendMsg(clienComSock, "True")

        #Check if socket is already associated with username
        if account["username"] in usernameToSockDic:
            sendMsg(clienComSock, "False")
            print("Account \'" + str(account["username"]) + "\' already logged in to", usernameToSockDic[account["username"]].getpeername())
            print(f"Ending connection with {cliInfo}\n")
        
        else:
            sendMsg(clienComSock, "True")

            #The username to socket   
            usernameToSockDic[account["username"]] = clienComSock

            #Say Hello
            name = account["nameF"]
            sendMsg(clienComSock, f"Hello, {name}.\n")
            
            #Create a new thread
            cliThread = threading.Thread(target=serviceClient, args=(clienComSock,account,))
            
            #Start the thread
            cliThread.start()

    else:
        sendMsg(clienComSock, "False")
        print(f"Account not found.\nEnding connection with {cliInfo}\n")