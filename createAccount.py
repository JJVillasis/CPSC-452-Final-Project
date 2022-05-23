from Crypto.Hash import SHA256
from getpass import getpass
import json

def createAccount(username, name, password, fileDSA, fileRSA, email):
    loadedjson = json.load(open("Accounts.json", "r"))

    for accounts in loadedjson:
        #Create account dictionary
        credentials = {}
        credentials["userid"] = len(loadedjson["Accounts"])+1
        credentials["username"] = username
        credentials["nameF"] = name.split()[0]
        credentials["nameL"] = name.split()[1]
        credentials["password"] = SHA256.new(password.encode()).hexdigest()
        credentials["publicDSA"] = fileDSA
        credentials["publicRSA"] = fileRSA
        credentials["email"] = email

        #Append to accounts list
        loadedjson[accounts].append(credentials)

    #Overwrite json file
    file = open("Accounts.json", "w")
    json.dump(loadedjson, file)
    file.close

print("".center(50, "="))
print("Create an account".center(50))
print("".center(50, "="), "\n")


username = input("Enter username: ")
name = input("Enter name (first last): ")

while True:
    print()
    password = getpass("Enter password for account: ")

    #Confirm password
    if password == getpass("Confirm password: "):
        print()
        break

    print("Passwords do not match. Try Again.")
    continue

fileDSA = input("Enter DSA public-key file: ")
fileRSA = input("Enter RSA public-key file: ")
email = input("Enter email address: ")

createAccount(username, name, password, fileDSA, fileRSA, email)

print("\nCreation Complete!\n")