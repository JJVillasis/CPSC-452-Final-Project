from Crypto.PublicKey import DSA, RSA
from getpass import getpass
from time import sleep

def generateKeyPair(keyType, fileNamePR, fileNamePU, passwordPR):

    #Generate DSA key Pair
    if keyType.lower() == "dsa":
        PR = DSA.generate(1024)
        PU = PR.publickey()

        #Write key pair into files
        with open (fileNamePR, "wb") as file:
            if passwordPR:
                file.write(PR.exportKey("PEM", True, passwordPR))
                file.close()
            else: 
                file.write(PR.exportKey("PEM"))
                file.close()

        with open (fileNamePU, "wb") as file:
            file.write(PU.exportKey("PEM"))
            file.close()

        return True

    #Generate RSA key Pair
    elif keyType.lower() == "rsa":
        PR = RSA.generate(1024)
        PU = PR.publickey()

        #Write key pair into files
        with open (fileNamePR, "wb") as file:
            if passwordPR:
                file.write(PR.export_key("PEM", passwordPR))
                file.close()
            else: 
                file.write(PR.export_key("PEM"))
                file.close()

        with open (fileNamePU, "wb") as file:
            file.write(PU.export_key("PEM"))
            file.close()

        return True

    #Unknown keyType
    else:
        return False

print("".center(50, "="))
print("Generate Key Pair (RSA/DSA)".center(50))
print("".center(50, "="), "\n")

#Get user arguments
keyType = input("Enter public-key type (DSA/RSA): ")
filePR = input("Enter filename for private-key (.pem): ")
filePU = input("Enter filename for public-key (.pem): ")

while True:
    print()
    password = getpass("Enter password for private-key (None - no pass): ")

    if password.lower() != "none":
        #Confirm password
        if password == getpass("Confirm password: "):
            print()
            break

        print("Passwords do not match. Try Again.")
        continue

    password = ""
    print()
    break

print("Generating public-key pair...")
sleep(1)

if generateKeyPair(keyType, filePR, filePU, password):
    print("Generation complete! Place files in their respective folders.\n")
    exit(1)
else:
    print("ERROR: Generation failed.\n")
