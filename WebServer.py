#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import socket
import threading


def connectionHandler(clientSocket, addr):
    while True:
        try:
            # Receive a message from the client
            message = clientSocket.recv(2048).decode()

            if message != '\r\n':
                try:
                    # Assume we have a HTTP GET message
                    filename = message.split()[1][1:]
                except:
                    # The client is sending unexpected messages. Break out of the loop
                    break

                print('File requested: ' + filename + ' ' + str(addr))

                with open(filename, 'r') as f:
                    outputdata = f.read()

                # Send the HTTP header into the socket
                clientSocket.send('HTTP/1.1 200 OK\r\n'.encode())
                clientSocket.send('Content-Type: text/html\r\n'.encode())
                clientSocket.send('Connection: keep-alive\r\n'.encode())
                clientSocket.send(('Content-Length: ' + str(len(outputdata.encode('utf-8'))) + '\r\n').encode())
                clientSocket.send('\r\n'.encode())

                # Send the content of the requested file to the client
                clientSocket.send((outputdata + '\f\r\n').encode())

        except IOError:
            # Send response message for file not found
            clientSocket.send('HTTP/1.1 404 Not Found\r\n'.encode())
            clientSocket.send('\r\n'.encode())

            # Close client socket and break out of the loop
            print('Could not serve file ' + str(addr))
            break

    print('Closing client socket ' + str(addr))
    clientSocket.close()


# Initialize configuration
config = configparser.ConfigParser()
config.read('config.cfg')
config = config['DEFAULT']

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Prepare a sever socket
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((config['defaultServerAddr'], int(config['defaultPort'])))

serverSocket.listen(int(config['backlog']))
print('Ready to serve...')

threads = []

while True:
    # Establish the connection
    clientSocket, addr = serverSocket.accept()
    print('Got connection from ' + str(addr))
    newThread = threading.Thread(target=connectionHandler, args=(clientSocket, addr))
    newThread.start()
    threads.append(newThread)

# Join the threads and close the socket
print('Server exiting.')
for thread in threads:
    thread.join()
serverSocket.close()
