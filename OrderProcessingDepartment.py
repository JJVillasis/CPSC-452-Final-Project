from Crypto.Hash import SHA256
from Crypto.PublicKey import DSA, RSA
from Crypto.Signature import DSS, pkcs1_15
from datetime import datetime
import json
import socket
import sys
import threading
from time import sleep

class OrderProcessingDepartment():

    def __init__(self, HOST, PORT):

        self.file = "inventory.json"

        self.HOST = HOST
        self.PORT = PORT

        #The socket the server uses for listening
        self.listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Bind socket to specified
        self.listenSock.bind((self.HOST, self.PORT))

        print("".center(50,"="))
        print(f" Listening on {(self.HOST, self.PORT)} ".center(50, "="))
        print("".center(50,"="), "")

        #Start listening with a connection backlog queue of 100
        self.listenSock.listen(100)

        #The user name to socket dictionary
        self.usernameToSockDic = {}

        self.serverLoop()

#################### Server Loop ####################

    def serverLoop(self):

        while True:
    
            #Accept the connection
            clienComSock, cliInfo = self.listenSock.accept()

            print()
            print("".center(50,"="))
            print(f" New client connected: {cliInfo} ".center(50, "="))
            print("".center(50,"="), "\n")
            
            #Get the username and password
            #Check if account exists in account records
            account = self.verifyAccount(self.recvMsg(clienComSock).decode(), self.recvMsg(clienComSock).decode())

            sleep(1)
            if account:
                
                #send that account is found
                print(f"{cliInfo}: Account verified.")
                self.sendMsg(clienComSock, "True")

                #Check if username is already associated with a socket
                if account["username"] in self.usernameToSockDic:
                    self.sendMsg(clienComSock, "False")
                    print(f"{cliInfo}: Account \'" + str(account["username"]) + "\' already logged in to", self.usernameToSockDic[account["username"]].getpeername())
                    print(f"{cliInfo}: Ending connection.")
                
                else:
                    self.sendMsg(clienComSock, "True")

                    #The username to socket   
                    self.usernameToSockDic[account["username"]] = clienComSock

                    #Say Hello
                    name = account["nameF"]
                    self.sendMsg(clienComSock, f"Hello, {name}.")
                    
                    #Create a new thread
                    cliThread = threading.Thread(target=self.serviceClient, args=(clienComSock,account,))
                    
                    #Start the thread
                    cliThread.start()

            else:
                self.sendMsg(clienComSock, "False")
                print(f"{cliInfo}: Account not found.{cliInfo}: Ending connection.")

    #############################################################################
    # serviceClient - Will be called by the thread that handles a single client #
    # @param clisock - the client socket                                        #
    # @param username - the user name to serve                                  #
    #############################################################################
    def serviceClient(self, cliSock, account):

        # Keep servicing the client until it disconnects
        while cliSock:

            #Send inventory to client
            self.sendMsg(cliSock, self.processInventory())
            print(f"{cliSock.getpeername()}: Sent inventory.")

            #Get order
            order = self.recvMsg(cliSock)

            #Check if client is ending connection
            if order.decode().lower() == "quit":
                self.sendMsg(cliSock, order.decode()) 
                break 

            #signature type, signature, and timestamp
            signType = self.recvMsg(cliSock)
            signature = self.recvMsg(cliSock)
            timestamp = self.recvMsg(cliSock).decode()
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

            #Verify order
            print(f"{cliSock.getpeername()}: Verifying order.")
            
            sleep(1)
            if self.verifyMessage(signType.decode(), order, signature, account):

                self.sendMsg(cliSock, "True")

                #Compare timestamps
                currentTime = datetime.now()
                timeDiff = currentTime - timestamp

                #Ensure order is not an hour old or older
                if int(timeDiff.seconds / 3600) < 1:
                    #Message signature verified
                    print(f"{cliSock.getpeername()}: Message verified")
                    self.sendMsg(cliSock, "True")

                    #Print retreived order
                    print(f"{cliSock.getpeername()}: Recieved Order: {order.decode()} at {timestamp}.")

                    #Process Order
                    print(f"{cliSock.getpeername()}: Processing order.")
                    sleep(1)
                    if self.processOrder(order.decode()):
                        print(f"{cliSock.getpeername()}: Order successfully processed.")
                        self.sendMsg(cliSock, "True")
                        continue

                    print(f"{cliSock.getpeername()}: Order failed.")
                    self.sendMsg(cliSock, "False")
                    continue

            #Message signature rejected or Timestamp too old
            print("Message invalidated")
            self.sendMsg(cliSock, "False")
            break

        #Connection ended with client
        print(f"{cliSock.getpeername()}: Ending connection.")

        #Remove Socket from dictionary
        del self.usernameToSockDic[account["username"]]


#################### Server Account Verification ####################

    ########################################################
    # getID - find if username is found in account records #
    # @param username - the name to search for             #
    # @returns account if found, or False is not           #
    ########################################################
    def getID(self, username):
        
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
    def verifyAccount(self, username, password):
        
        #Check username
        account = self.getID(username)
        
        #Check if account exists
        if account:
            
            #Find sha256 hash of password
            hashedPass = SHA256.new(password.encode())
            hexDig = hashedPass.hexdigest()

            #Check if password is found
            if hexDig == account["password"]:
                return account
        
        return False

#################### Server Send/Recieve ####################

    ########################################################
    # getID - find if username is found in account records #
    # @param username - the name to search for             #
    # @returns account if found, or False is not           #
    ########################################################
    def getID(self, username):
        
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
    def verifyAccount(self, username, password):
        
        #Check username
        account = self.getID(username)
        
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
    def sendMsg(self, sock, msg):

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
    def recvMsg(self, sock):
        
        #The size
        size = sock.recv(3)
        
        #Convert the size to the integer
        intSize = int(size)

        #Receive the data
        data = sock.recv(intSize)

        return data

#################### Server Digital Signature ####################

    ####################################################################
    # verifyMessage - Verify the signature of a message using RSA/DSA. #
    # @param signType - The digital signature scheme to be used.       #
    # @param message - The message to be signed.                       #
    # @param signature - Possible signature associated with message.   #
    # @param account - account of the client                           #
    # @returns if verification succeed.                                #
    ####################################################################
    def verifyMessage(self, signType, message, signature, account):

        #DSA Signature Verification
        if signType.upper() == "DSA":
            return self.verifyDSA(message, signature, account["publicDSA"])

        #RSA Signature Verification
        elif signType.upper() == "RSA":
            return self.verifyRSA(message, signature, account["publicRSA"])

        #Unknown Scheme
        else:
            return False

    ##################################################################
    # verifyDSA - Use DSA to verify a message with a signature.      #
    # @param message - The message to be signed.                     #
    # @param signature - Possible signature associated with message. #
    # @param keyFile - The file name of the PEM that stores the key. #
    # @returns if verification succeed.                              #
    ##################################################################
    def verifyDSA(self, message, signature, keyFile):

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
    def verifyRSA(self, message, signature, keyFile):
        
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

#################### Server Order Processing ####################

    #######################################################
    # processInventory - Convert inventory json to string #
    #######################################################
    def processInventory(self):

        #Open inventory
        inventory = json.load(open(self.file, "r"))
        
        #Create Inventory string 
        invStr = ""
        for category in inventory:
            for catID in category:
                invStr += f" {catID} ".center(50, "=") + "\n"
                for item in category[catID]:
                    itemDes = item["itemName"] + " (" + str(item["itemCount"]) + ")"
                    invStr += itemDes.ljust(40, " ") + str(item["itemCost"]).rjust(10, " ") + "\n"
                invStr += "\n"
        return invStr


    #################################################
    # checkInventory - Check product availability   #
    # @param product - Product to be checked        #
    # @returns if product is available in inventory #
    #################################################
    def checkInventory(self, product):

        #Open inventory
        inventory = json.load(open(self.file, "r"))

        for category in range(len(inventory)):
            for catID in inventory[category]:
                for item in range(len(inventory[category][catID])):
                    if inventory[category][catID][item]["itemName"].lower() == product.lower():
                        return category, catID, item

        return False

    
    ############################################################
    # processOrder - Process customer order, send email        #
    # @param order - Order to be processed                     #
    # @returns if order was successfully processed             #
    ############################################################
    def processOrder(self, order):

        inventory = json.load(open(self.file, "r"))

        #Check product availability
        if product := self.checkInventory(order):
            category = product[0]
            catID = product[1]
            item = product[2]

            inventory[category][catID][item]["itemCount"] -= 1

            #If item was last in stock, remove item from inventory
            if inventory[category][catID][item]["itemCount"] == 0:
                del inventory[category][catID][item]

            #Update inventory
            file = open(self.file, "w")
            json.dump(inventory, file)
            file.close()

            return True

        #Product not found
        return False