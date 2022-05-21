import sys
from OrderProcessingDepartment import OrderProcessingDepartment

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

OrderProcessingDepartment(HOST, PORT)