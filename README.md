# CPSC 452: Final Project - Secure Purchase Order
## Description
Implement a secure purchase order system that allows the user to enter a purchase request and routes it to Order Processing Department (OPD) for signature. Each customer has an account with the online purchasing system. The online purchasing system has the public-key of every customer.

First, the customer enters his/her ID and password. The system verifies his/her ID and password. Next, the customer sends the order as well as a timestamp to the OPD - confidentiality and digital signature must be provided. OPD verifies the signature of the customer and checks if the product is available. If the customer’s signature is verified and the product is available, OPD prepares the order. After OPD processes the order, OPD retrieves the customers email address and sends an email to the customer, indicating that the order has been shipped. OPD should be implemented as a concurrent server.

Your implementation must provide both confidentiality and digital signature. For digital signature you must provide the user with a choice of using RSA or Digital Signature Algorithm (DSA; https://bit.ly/2TvvGSt). Both digital signature schemes must be supported.

## Group Members:
Benjamin Ahn - benahn333@csu.fullerton.edu

Lyba Batla - lybabatla@csu.fullerton.edu

Casey Thatsanaphonh - cthatsanaphonh@csu.fullerton.edu

Joshua Villasis - JJVillasis@csu.fullerton.edu

Evan Wu - Evanh.wu@csu.fullerton.edu

Po-Tyng (Peter) Wu - gaidepeter@csu.fullerton.edu

## Programming Language:
3.10

## How to Execute (Server):
In a command terminal, change the directory so that it may point to the project folder.

To run the host server, enter `python Server.py <HOST ADDRESS> <PORT>` into the terminal. Where:
- `HOST ADDRESS`: The IP address the server binds to
- `PORT`: Network port the server listens to

If the user wishes to listen to all addresses in a port, they can enter `python Server.py <PORT>`, and the server binds to the address "".

### Example: 
`python Server.py 127.0.0.1 2345` binds the server to the computer's local address "127.0.0.1" and listens to port "2345" for any client attempting to connect.

or 

`python Server.py 2345` listens to all addresses in port "2345" for any client attempting to connect

## How to Execute (Client)
In a command terminal seperate from a terminal running the server,  once again change the directory so that it may point to the project folder.

To join the server as a client, enter `python Client.py <HOST ADDRESS> <PORT>` into the terminal. Where:
- `HOST ADDRESS`: The IP address the host server is bound to
- `PORT`: Network port the host server is listening to

### Example: 
`python Client.py 127.0.0.1 2345` connects to the server via the computer's local address "127.0.0.1" and  port "2345".
