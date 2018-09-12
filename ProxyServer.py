#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import socket
import sys
import time

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    sys.exit(2)

server_ip = sys.argv[1]

# Initialize configuration
config = configparser.ConfigParser()
config.read('config.cfg')
config = config['DEFAULT']

# Create & prepare a server socket, bind it to a port and start listening
tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpSerSock.bind((config['defaultServerAddr_proxy'], int(config['defaultPort'])))
tcpSerSock.listen(int(config['backlog']))

while 1:
    # Start receiving data from the client
    print('Ready to serve...')

    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

    message = tcpCliSock.recv(2048).decode()
    print(message)

    # Extract the filename from the given message
    print(message.split()[1])
    filename = message.split()[1].partition("/")[2]
    filename = filename[1:-1]
    print(filename)

    fileExist = "false"
    filetouse = "proxy_cache/" + filename
    print(filetouse)

    try:
        # Check wether the file exist in the cache
        f = open(filetouse, "r")
        outputdata = f.read()
        fileExist = "true"

        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.send('HTTP/1.1 200 OK\r\n'.encode())
        tcpCliSock.send('Content-Type: text/html\r\n'.encode())
        tcpCliSock.send('\r\n'.encode())

        # tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
        # tcpCliSock.send("Content-Type:text/html\r\n".encode())
        # tcpCliSock.send("\r\n".encode())
        tcpCliSock.send((outputdata + '\r\n').encode())

        print('Read from cache')

    # Error handling for file not found in cache
    except IOError:
        if fileExist == "false":
            # Create a socket on the proxyserver
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            c.settimeout(float(config['recvDelay']))

            hostn = filename.replace("www.","",1)
            print(hostn)
            try:
                # Connect to the socket to port 80
                c.connect((server_ip, 80))

                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                # fileobj = c.makefile('r', 0)
                # fileobj.write("GET " + filename + " HTTP/1.0\n\n")

                get_request = 'GET /' + str(filename) + ' HTTP/1.1\r\n'
                c.send(get_request.encode())
                c.send('\r\n'.encode())


                # Ensure all messages are received
                target_time = time.time() + float(config['recvDelay'])
                while target_time > time.time():
                    with open("proxy_cache/" + str(filename), "w") as tmpFile:
                        # Read the response into buffer
                        try:
                            buffer = c.recv(2048).decode()
                        except:
                            pass

                        # Create a new file in the cache for the requested file.
                        # Also send the response in the buffer to client socket and the corresponding file in the cache
                        tmpFile.write(buffer)

            except:
                print("Illegal request")
    else:
        # HTTP response message for file not found
        tcpCliSock.send('HTTP/1.1 404 Not Found\r\n'.encode())
        tcpCliSock.send('\r\n'.encode())

# Close the client and the server sockets
tcpCliSock.close()
c.close()