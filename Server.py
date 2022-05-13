import socket
import threading

#Host IP and Port
listenHost = ""
listenPort = 1234

#The socket the server uses for listening
listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Associate the listening socket with port 1234
listenSock.bind((listenHost, listenPort))

print(f"Listening on {(listenHost, listenPort)}.\n")

#Start listening with a connection backlog queue of 100
listenSock.listen(100)

#The user name to socket dictionary
userNameToSockDic = {}

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
# @param userName - the user name to serve                                  #
#############################################################################
def serviceClient(cliSock, userName):

    # Keep servicing the client until it disconnects
    while cliSock:
    
        # Receive the data from the client
        cliData = recvMsg(cliSock)

        #Check if client ended conneciton
        if cliData.decode() == "goodbye":
            sendMsg(cliSock, cliData.decode()) 
            break
    
        print(f"Got data {cliData} from client socket {cliSock.getsockname()}")
        
        # Send the capitalized string to the client
        sendMsg(cliSock, "Hello, " + userName.decode())
    
        # Hang up the client
        #cliSock.close()
    print(f"Ending connection with {cliSock.getsockname()}")
    


# Server loop
while True:
    
    # Accept the connection
    clienComSock, cliInfo = listenSock.accept()

    print("New client connected: ", cliInfo)
    
    # Get the user name
    userName = recvMsg(clienComSock)    
    
    print("Got user name", userName)
    
    # The user name to socket   
    userNameToSockDic[userName] = clienComSock
    
    # Create a new thread
    cliThread = threading.Thread(target=serviceClient, args=(clienComSock,userName,))
    
    # Start the thread
    cliThread.start()