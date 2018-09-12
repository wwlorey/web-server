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

    # Extract the fileName from the given message
    fileName = message.split()[1].partition('/')[2].replace('/', '').replace('www.', '')
    print(fileName)

    fileExist = False
    fileToUse = fileName

    try:
        # Check wether the file exists in the cache
        if fileToUse:
            with open(fileToUse, 'r') as f:
                outputdata = f.read()

            fileExist = True

            # ProxyServer finds a cache hit and generates a response message
            tcpCliSock.send('HTTP/1.1 200 OK\r\n'.encode())
            tcpCliSock.send('Content-Type: text/html\r\n'.encode())
            tcpCliSock.send('Connection: keep-alive\r\n'.encode())
            tcpCliSock.send(('Content-Length: ' + str(len(outputdata.encode('utf-8'))) + '\r\n').encode())
            tcpCliSock.send('\r\n'.encode())

            # Send the content of the requested file to the client
            tcpCliSock.send((outputdata + '\f\r\n').encode())

            print('Read from cache')

    # Error handling for file not found in cache
    except IOError:
        if not fileExist:
            # Create a socket on the proxyserver
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            c.settimeout(float(config['recvDelay']))

            print(server_ip)
            hostName = server_ip.replace('http://', '')

            if hostName[-1] == '/':
                hostName = hostName[:-1]

            domain_ending_index = max(hostName.find('.com'), hostName.find('.edu'), hostName.find('.net'))
            if domain_ending_index > 0:
                print(hostName)
                subDomain = hostName[domain_ending_index + 4:]
                hostName = hostName[:domain_ending_index + 4]
            else:
                subDomain = '/'
            
            try:
                # Connect to the socket to port 80
                c.connect((hostName, 80))

                # get_request = 'GET ' + str(subDomain) + '/' + str(fileName) + ' HTTP/1.1\r\n'
                get_request = ''
                get_request +=    'GET ' + str(subDomain) + '/' + str(fileName) + ' HTTP/1.1\r\n'
                get_request +=    'Host: ' + str(hostName) + '\r\n'
                get_request +=    'Connection: keep-alive\r\n'
                get_request +=    'Upgrade-Insecure-Requests: 1\r\n'
                get_request +=    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n'
                get_request +=    'Accept-Language: en-US,en;q=0.9\r\n'

                c.send(get_request.encode())
                c.send('\r\n'.encode())
                print(get_request)
                
                if fileName:
                    with open(fileName, 'w') as tmpFile:
                        # Read the response into buffer
                        buffer = ''
                        while True:
                            try:
                                buffer += c.recv(2048).decode()
                                # print('RECEIVED FROM TAYLOR:')
                                # print(buffer)
                            except:
                                break

                        # Also send the response in the buffer to client socket and the corresponding file in the cache
                        if buffer:
                            write = False
                            html_buffer = ''
                            for line in buffer.split('\r\n'):
                                if line == '':
                                    # Record all following lines
                                    write = True

                                if write:
                                    html_buffer += line

                            tmpFile.write(html_buffer)

                            tcpCliSock.send('HTTP/1.1 200 OK\r\n'.encode())
                            tcpCliSock.send('Content-Type: text/html\r\n'.encode())
                            tcpCliSock.send('Connection: keep-alive\r\n'.encode())
                            tcpCliSock.send(('Content-Length: ' + str(len(html_buffer.encode('utf-8'))) + '\r\n').encode())
                            tcpCliSock.send('\r\n'.encode())

                            # Send the content of the requested file to the client
                            tcpCliSock.send((html_buffer + '\f\r\n').encode())


            except:
                print("Illegal request")

    else:
        # HTTP response message for file not found
        tcpCliSock.send('HTTP/1.1 404 Not Found\r\n'.encode())
        tcpCliSock.send('\r\n'.encode())

# Close the client and the server sockets
tcpCliSock.close()
c.close()