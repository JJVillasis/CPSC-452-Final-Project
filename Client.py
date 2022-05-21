import sys
from OPDClient import OPDClient

#Parse command line to get <HOST> and <PORT>
if len(sys.argv) != 3:
    print("ERROR: User must specify <HOST ADDRESS> and <PORT>.\n")
    exit(-1)

#The remote host
HOST, PORT = sys.argv[1], int(sys.argv[2])

OPDClient(HOST, PORT)