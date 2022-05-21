from Crypto.Hash import SHA256
from Crypto.PublicKey import DSA, RSA
from Crypto.Signature import DSS, pkcs1_15
from getpass import getpass
import json
import socket
from time import sleep

class OPDClient():

    def __init__(self, address):
        self.HOST = address[0]
        self.PORT = address[1]

        print(f"Connecting to {(self.HOST, self.PORT)}...\n")
        sleep(1)

        #Establish client Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Connect to host server
        self.sock.connect((self.HOST, self.PORT))
        print("Connection successful!\n")

        #Login to OPD
        self.accountLogin()
        self.orderLoop()

#################### Client Account Login ####################

    def accountLogin(self):
        
        #Login to server
        print("".center(50,"="))
        print("LOG INTO YOUR ACCOUNT:".center(50))
        print("".center(50,"-"))
        self.username = input("Username: ")
        self.sendMsg(self.sock, self.username)
        self.sendMsg(self.sock, getpass("Password: "))

        print("\nVerifying account...")

        #Verify account
        if self.recvMsg(self.sock).decode() == "False":
            print("ERROR: <USERNAME> or <PASSWORD> not found.\n")
            return False

        #Check if account is logged in to another socket
        if self.recvMsg(self.sock).decode() == "False":
            print("ERROR: Account logged in to another socket.\n")
            return False

        #Server Hello and inventory json
        print("Account Found!")
        print("".center(50,"="), "\n")
        print(self.recvMsg(self.sock).decode())
        self.jsonFile = self.recvMsg(self.sock).decode()
        print("Recieved Inventory\n")

#################### Client Order Loop ####################

    def orderLoop(self):

         while True:

            print("".center(50,"="))

            ########## Digital Signature ##########

            #Get type and message
            message = input("Send something to the Host: ")
            signType = input("Digital Signature type (DSA/RSA): ")

            #Sign message
            signature = self.signMessage(signType, message, self.username, getpass("Password to key ('None' if not used): "))

            #Send type, message, and signature to Server
            self.sendMsg(self.sock, signType)
            self.sendMsg(self.sock, message)
            self.sendSign(self.sock, signature)

            print("\nVerifying Message...")

            #Check if message is verified
            if self.recvMsg(self.sock).decode() == "True":
                print("Message verified.")

                data = self.recvMsg(self.sock)

                #End connection with host
                if data.decode() == "goodbye":
                    print(f"Connection ended with {self.sock.getsockname()}. Goodbye.")
                    print("".center(50,"="), "\n")
                    break

                print(f"Received: {data.decode()}\n")

            else:
                print("Message invalidated.")
                print("".center(50,"="), "\n")
                break

            print("".center(50,"="), "\n")

#################### Client Send/Receive ####################

    ################################################
    # recvMsg - The function to handle the message #
    #             of the specified format          #
    # @param sock - socket to receive message      #
    # @returns the message without the header      #
    ################################################
    def recvMsg(self, sock):
        
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
    def sendMsg(self, sock, msg):

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

    #################################################
    # sendSign - Format given signature, send it to #
    #             the host server.                  #
    # @param sock - The socket to the signature.    #
    # @param sign - The signature to be sent.       #
    #################################################
    def sendSign(self, sock, sign):

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

#################### Client Digital Signature ####################

    ##############################################################
    # signMessage - Signs a message using DSA/RSA.               #
    # @param signType - The digital signature scheme to be used. #
    # @param message - The message to be signed.                 #
    # @param username - Username of Account.                     #
    # @param password - Password to the key (if used).           #
    # @returns signature associated with the message.            #
    ##############################################################

    def signMessage(self, signType, message, username, password):
        
        #Get file name
        file = "private" + username + signType.upper() + ".pem"

        #DSA Digital Signature
        if signType.upper() == "DSA":
            return self.signDSA(message, file, password)

        #RSA Digital Signature
        elif signType.upper() == "RSA":
            return self.signRSA(message, file, password)

        #Unknown Scheme
        else:
            return False

    ##################################################################
    # signDSA - Use DSA to sign a message.                           #
    # @param message - The message to be signed.                     #
    # @param keyFile - The file name of the PEM that stores the key. #
    # @param password - Password to the key (if used).               #
    # @returns signature associated with the message.                #
    ##################################################################

    def signDSA(self, message, keyFile, password):

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

    ##################################################################
    # signRSA - Use RSA to sign a message.                           #
    # @param message - The message to be signed.                     #
    # @param keyFile - The file name of the PEM that stores the key. #
    # @param password - Password to the key (if used).               #
    # @returns signature associated with the message.                #
    ##################################################################

    def signRSA(self, message, keyFile, password):
        
        #Retrieve private key
        with open("Private Key PEMs/" + keyFile, "rb") as file:
            if password.lower() == "none":
                PR = RSA.import_key(file.read())
            elif password:
                PR = RSA.import_key(file.read(), password)

        #Get message hash
        hashedMessage = SHA256.new(message.encode())

        #Sign message
        signature = pkcs1_15.new(PR).sign(hashedMessage)

        return signature


    def printInventory(self, jsonName):
        invJson = json.load(open(jsonName))

        for inventory in invJson:
            for category in inventory:
                print(f" {category} ".center(50, "="))
                for item in inventory[category]:
                    itemDes = item["itemName"] + " (" + str(item["itemCount"]) + ")"
                    print(itemDes.ljust(40, " ") + str(item["itemCost"]).rjust(10, " "))
                print()