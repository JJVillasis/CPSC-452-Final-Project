from hashlib import sha256
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
    
    account = getID(username)
    
    #Check if account exists
    if account:
        
        #Find sha256 hash of password
        hashedPass = sha256(password.encode())
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


#############################################################################
# serviceClient - Will be called by the thread that handles a single client #
# @param clisock - the client socket                                        #
# @param username - the user name to serve                                  #
#############################################################################
def serviceClient(cliSock, username):

    # Keep servicing the client until it disconnects
    while cliSock:
    
        # Receive the data from the client
        cliData = recvMsg(cliSock)

        #Check if client ended conneciton
        if cliData.decode() == "goodbye":
            sendMsg(cliSock, cliData.decode()) 
            break
    
        print(f"Got data {cliData} from client socket {cliSock.getsockname()}\n")
        
        # Echo message to client
        sendMsg(cliSock, "Echo: " + cliData.decode())

    #Connection ended with client
    print(f"Ending connection with {cliSock.getsockname()}\n")

    #Remove Socket from dictionary
    del usernameToSockDic[username]


#################### Server Loop ####################

while True:
    
    #Accept the connection
    clienComSock, cliInfo = listenSock.accept()

    print(f"New client connected: {cliInfo}")
    
    #Get the username and password
    #Check if account exists in account records
    account = verifyAccount(recvMsg(clienComSock).decode(), recvMsg(clienComSock).decode())

    sleep(2)
    if account:
        
        #send that account is found
        print("\nAccount verified.\n")
        sendMsg(clienComSock, "TRUE")

        #Check if socket is already associated with username
        if account["username"] in usernameToSockDic:
            sendMsg(clienComSock, "FALSE")
            print(f"Account {account["username"]} already logged in to {usernameToSockDic[account["username"].getsockname()]}.\nEnding connection with {cliInfo}\n")
        
        else:
            sendMsg(clienComSock, "TRUE")

            #The username to socket   
            usernameToSockDic[account["username"]] = clienComSock

            #Say Hello
            name = account["nameF"]
            sendMsg(clienComSock, f"Hello, {name}.\n")
            
            #Create a new thread
            cliThread = threading.Thread(target=serviceClient, args=(clienComSock,account["username"],))
            
            #Start the thread
            cliThread.start()

    else:
        sendMsg(clienComSock, "FALSE")
        print(f"Account not found.\nEnding connection with {cliInfo}\n")