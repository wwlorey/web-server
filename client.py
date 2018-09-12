#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import socket
import sys
import time

# Initialize configuration
config = configparser.ConfigParser()
config.read('config.cfg')
config = config['DEFAULT']

# Read command line arguments
if len(sys.argv) == int(config['numExpectedArgs']):
    serverAddr = sys.argv[int(config['serverAddrArgIndex'])]
    port = int(sys.argv[int(config['portArgIndex'])])
    fileName = sys.argv[int(config['fileNameArgIndex'])]
else:
    # Default to the values in config
    serverAddr = config['defaultServerName']
    port = int(config['defaultPort'])
    fileName = config['defaultFileName']


exit_client = False

# Create the client socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.settimeout(float(config['recvDelay']))

# Establish the connection
clientSocket.connect((serverAddr, port))

while True:
    # Get the file name from the user
    file_name = input('Enter file name ("exit" to exit): ')
    if file_name == 'exit':
        break

    # Request the file from the server
    get_request = 'GET /' + str(file_name) + ' HTTP/1.1\r\n'
    clientSocket.send(get_request.encode())
    clientSocket.send('\r\n'.encode())

    # Ensure all messages are received
    target_time = time.time() + float(config['recvDelay'])
    while target_time > time.time():
        try:
            # Receive and decode the message
            file_contents = clientSocket.recv(2048).decode()

            # Only print the message if it is not empty
            if file_contents:
                print(file_contents)

            if '404 Not Found' in file_contents:
                # The file was not found by the server
                exit_client = True
                break

        except:
            # Handle the client socket receive timeout
            pass
    
        if exit_client:
            break

# Close the socket and exit the program
print('Client exiting.')
clientSocket.close()
sys.exit()