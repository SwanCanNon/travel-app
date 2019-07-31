#Author: Alan Paniagua
#PID: 2114765
#Course: COP 4338
#clientTravel.py: A simple command-line client to interact with the server.

import socket

BUFFSIZE = 4096
SERVER = 'localhost'
PORT = 10001    #Port to use, per assignment

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))


while True:
    out_data = ''
    in_data =  client.recv(BUFFSIZE)

    print(in_data.decode())

    while not out_data:
        out_data = input('Enter a command: ')

    client.sendall(bytes(out_data,'UTF-8'))

    if out_data=='QUIT':
        print("Connection has been closed. Thank you for using Alan Airlines.")
        break


client.close()
