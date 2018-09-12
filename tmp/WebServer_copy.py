#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import socket
import sys

from email.utils import formatdate

# Initialize configuration
config = configparser.ConfigParser()
config.read('config.cfg')
config = config['DEFAULT']

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Prepare a sever socket
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((config['serverName'], int(config['port'])))

serverSocket.listen(2)

# Establish the connection
print('Ready to serve...')
clientSocket, addr = serverSocket.accept()

while True:
    try:
        message = clientSocket.recv(2048).decode()

        if message != '\r\n':
            try:
                # Assume we have a HTTP GET message
                filename = message.split()[1][1:]
            except:
                # The client is sending unexpected messages. Break out of the loop
                break

            print('File requested: ' + filename)

            with open(filename, 'r') as f:
                outputdata = f.read()

            # Send HTTP header lines into socket
            # clientSocket.send(''.encode())

            clientSocket.send('HTTP/1.1 200 OK\r\n'.encode())
            # clientSocket.send(('Date: ' + formatdate(timeval=None, localtime=False, usegmt=True) + '\r\n').encode())
            # clientSocket.send('Server: Apache/2.4.18 (Ubuntu)\r\n'.encode())
            # clientSocket.send('Accept-Ranges: bytes\r\n'.encode())
            # clientSocket.send(('Content-Length: ' + str(sys.getsizeof(outputdata)) + '\r\n').encode())
            # clientSocket.send('Keep-Alive: timeout=10, max=100\r\n'.encode())
            # clientSocket.send('Connection: Keep-Alive\r\n'.encode())
            # clientSocket.send('Content-Type: text/html; charset=ISO-8859-1\r\n'.encode())
            # clientSocket.send('Accept-Ranges: bytes\r\n'.encode())
            # clientSocket.send(('Content-Length: ' + str(sys.getsizeof(outputdata)) + '\r\n').encode())
            clientSocket.send('Content-Type: text/html\r\n'.encode())
            # clientSocket.send(('File Data: ' + str(sys.getsizeof(outputdata)) + ' bytes\r\n').encode())
            clientSocket.send('Connection: keep-alive\r\n'.encode())
            clientSocket.send('Content-Length: 71\r\n'.encode())
            clientSocket.send('\r\n'.encode())
            # Send the content of the requested file to the client
            clientSocket.send((outputdata + '\f\r\n').encode())

    except IOError:
        pass
        # Send response message for file not found
        clientSocket.send('HTTP/1.1 404 Not Found\r\n'.encode())
        clientSocket.send('\r\n'.encode())

        # Close client socket and break out of the loop
        print('Closing client socket.')
        clientSocket.close()
        break

print('Server exiting.')
serverSocket.close()
sys.exit()