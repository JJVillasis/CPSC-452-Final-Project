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
