#Author: Alan Paniagua
#PID: 2114765
#Course: COP 4338

#serverTravel.py: A command-line server that simulates airlines ticket search and purchases.
#The server can be communicated to through clientTravel.py.
#The server and client only communicate using sockets and messages.
#Implemented commands are:
# LIST
# SEARCHD DEST
# SEARCHALL DEST
# SEARCHS DEPARTURE
# BUY_TICKET where seats
# BUYRT_TICKET where seats
# RETURN_TICKET where seats
# RETURNRT_TICKET where seats


import os
import socket
import threading

BUFFSIZE = 4096
flights = {}    #("departure", "destination"): ["seats", "price"]
locations = set()
HOST = '0.0.0.0'
PORT = 10001
lock = threading.RLock()
column_titles = '{0:6} -- {1:5} -- {2:5}'.format('Flights', 'Seats', 'Price')

help_message = """To see a list of all flights, type "LIST".
To search one-way flights with a specific destination, type "SEARCHD [destination]".
To search roundtrip flights with a specific destination, type "SEARCHALL [destination]".
To search one-way flights with a specific departure, type "SEARCHS [departure]".
To buy a one-way ticket, type "BUY_TICKET [where] [seats]".
To buy a roundtrip ticket, type "BUYRT-TICKET [where] [seats]".
To return a one-way ticket, type "RETURN_TICKET [where] [seats]".
To return a roundtrip ticket, type "RETURNRT_RICKET [where] [seats]".
[destination] and [departures] must be in the form of a 3-letter code. (ex: MIA)
[where] must be in the form of 3-letter codes, separated by a dash. (ex: MIA-ORL)
[seats] must be a number."""
welcome_message = "Welcome to Alan Airlines official travel app!\n\n" + help_message


class ClientThread(threading.Thread):
    

    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("New connection added: ", clientAddress)
        self.send_welcome_message()


    def run(self):
        print ("Connection from : ", clientAddress)
        msg = ''

        while True:
            data = self.csocket.recv(BUFFSIZE)
            msg = data.decode()
            print ("From client at {0}: ", clientAddress, msg)
            try:
                command_recognized = self.process_command(str.strip(msg))
                if command_recognized == -1:
                    break
                if not command_recognized:
                    self.csocket.sendall(bytes("Command was not recognized, please try again.\nCommand received: " + msg,'UTF-8'))
            except ValueError as e:
                self.csocket.sendall(bytes('Error! ' + str(e) + '\nCommand received: ' + msg,'UTF-8'))
                pass

        print("Client at ", clientAddress , " disconnected...")

    def not_valid_location(self, location):
        if location not in locations:
            return 1
        return 0

    def send_welcome_message(self):
        self.csocket.sendall(bytes(welcome_message, 'UTF-8'))

    def send_help_message(self):
        self.csocket.sendall(bytes(help_message, 'UTF-8'))

    def search_destination(self, dest):
        #Search for matching destination in flight dictionary.
        #("departure", "destination"): ["seats", "price"]
        #Assumes location is valid and present in dictionary.
        return_string = column_titles + '\n'

        for (sk, dk), [v1, v2] in sorted(flights.items()):
            if dk == dest:
                return_string += '{0:3}-{1:3}    {2:^5}   ${3:^5}\n'.format(sk, dk, v1, v2)

        self.csocket.sendall(bytes(str(return_string),'UTF-8'))

    def search_all(self, dest):
        #Search for matching departures and destinations in flight dictionary.
        #("departure", "destination"): ["seats", "price"]
        #Assumes locations are valid and present in dictionary.
        return_string = column_titles + '\n'
        
        for (sk, dk), [v1, v2] in sorted(flights.items()):
            if dk == dest or sk == dest:
                return_string += '{0:3}-{1:3}    {2:^5}   ${3:^5}\n'.format(sk, dk, v1, v2)

        self.csocket.sendall(bytes(str(return_string),'UTF-8'))

    def search_departures(self, departure):
        #Search for matching departures dictionary.
        #("departure", "destination"): ["seats", "price"]
        #Assumes location is valid and present in dictionary.
        return_string = column_titles + '\n'

        for (sk, dk), [v1, v2] in sorted(flights.items()):
            if sk == departure:
                return_string += '{0:3}-{1:3}    {2:^5}   ${3:^5}\n'.format(sk, dk, v1, v2)
        
        self.csocket.sendall(bytes(str(return_string),'UTF-8'))

    def buy_ticket(self, departure, dest, amount):
        #Simulates the purchase of a flight ticket.
        #("departure", "destination"): ["seats", "price"]
        #Assumes flight is valid and present in dictionary.
        if int(amount) < flights[(departure, dest)][0]:
            lock.acquire()
            flights[(departure, dest)][0] -= int(amount)
            lock.release()
        else:
            raise ValueError("There are not enough seats left to complete your purchase. Please try again.")

        return_string = 'You have purchased {0} one-way tickets to flight {1}-{2} for ${3}.'.format(amount, departure, dest, flights[(departure, dest)][1])
        self.csocket.sendall(bytes(str(return_string),'UTF-8'))

    def buy_roundtrip_ticket(self, departure, dest, amount):
        #Simulates the purchase of a flight ticket.
        #Purchases departure-dest ticket and dest-departure ticket.
        #("departure", "destination"): ["seats", "price"]
        #Assumes flight is valid and present in dictionary.
        if int(amount) < flights[(departure, dest)][0] and int(amount) < flights[(dest, departure)][0]:
            lock.acquire()
            flights[(dest, departure)][0] -= int(amount)
            flights[(departure, dest)][0] -= int(amount)
            lock.release()
        else:
            raise ValueError("There are not enough seats available for that trip.")

        return_string = 'You have purchased {0} roundtrip tickets to flight {1}-{2} for ${3}.'.format(amount, departure, dest, flights[(departure, dest)][1])
        self.csocket.sendall(bytes(str(return_string),'UTF-8'))

    def return_ticket(self, departure, dest, amount):
        #Simulates the return of a flight ticket.
        #("departure", "destination"): ["seats", "price"]
        #Assumes flight is valid and present in dictionary.
        lock.acquire()
        flights[(departure, dest)][0] += int(amount)
        lock.release()

        return_string = 'You have returned {0} one-way tickets to flight {1}-{2} for ${3}.'.format(amount, departure, dest, flights[(departure, dest)][1])
        self.csocket.sendall(bytes(str(return_string),'UTF-8'))

    def return_roundtrip_ticket(self, departure, dest, amount):
        #Simulates the return of a roundtrip flight ticket.
        #Return daprture-dest and dest-departure ticket.
        #("departure", "destination"): ["seats", "price"]
        #Assumes flight is valid and present in dictionary.
        lock.acquire()
        flights[(dest, departure)][0] += int(amount)
        flights[(departure, dest)][0] += int(amount)
        lock.release()

        return_string = 'You have returned {0} roundtrip tickets to flight {1}-{2} for ${3}.'.format(amount, departure, dest, flights[(departure, dest)][1])
        self.csocket.sendall(bytes(str(return_string),'UTF-8'))

    def process_command(self, msg):
        #Based on msg, executes appropriate command and returns status code.
        #Returns -1 if user wants to quit.
        #Returns 0 if command is not recognized.
        #Returns 1 if command has been recognized.
        #Checks for valid location arguments and minimum number of arguments,.
        splitmsg = msg.split(' ')

        if splitmsg[0] == 'QUIT':
            return -1
        elif splitmsg[0] == 'LIST':
            self.print_flights()
        elif splitmsg[0] == 'HELP':
            self.send_help_message()
        elif splitmsg[0] == 'SEARCHD':
            if len(splitmsg) < 2:
                raise ValueError("Missing argument, please try again.")
            elif splitmsg[1] not in locations:
                raise ValueError("Location code was not recognized, please try again.")
            self.search_destination(splitmsg[1])
        elif splitmsg[0] == 'SEARCHALL':
            if len(splitmsg) < 2:
                raise ValueError("Missing argument, please try again.")
            elif splitmsg[1] not in locations:
                raise ValueError("Location code was not recognized, please try again.")
            self.search_all(splitmsg[1])
        elif splitmsg[0] == 'SEARCHS':
            if len(splitmsg) < 2:
                raise ValueError("Missing argument, please try again.")
            elif splitmsg[1] not in locations:
                raise ValueError("Location code was not recognized, please try again.")
            self.search_departures(splitmsg[1])
        elif splitmsg[0] == 'BUY_TICKET':
            if len(splitmsg) < 3:
                raise ValueError("Missing argument, please try again.\n")
            if '-' in splitmsg[1]:
                tripsplit = splitmsg[1].split('-')
            else:
                raise ValueError("Trip argument not recognized. Make sure it is in the format XXX-YYY.")
            if tripsplit[0] not in locations or tripsplit[1] not in locations:
                raise ValueError("Location code was not recognized, please try again.")
            self.buy_ticket(tripsplit[0], tripsplit[1], splitmsg[2])
        elif splitmsg[0] == 'BUYRT_TICKET':
            if len(splitmsg) < 3:
                raise ValueError("Missing argument, please try again.\n")
            if '-' in splitmsg[1]:
                tripsplit = splitmsg[1].split('-')
            else:
                raise ValueError("Trip argument not recognized. Make sure it is in the format XXX-YYY.")
            if tripsplit[0] not in locations or tripsplit[1] not in locations:
                raise ValueError("Location code was not recognized, please try again.")
            self.buy_roundtrip_ticket(tripsplit[0], tripsplit[1], splitmsg[2])
        elif splitmsg[0] == 'RETURN_TICKET':
            if len(splitmsg) < 3:
                raise ValueError("Missing argument, please try again.\n")
            if '-' in splitmsg[1]:
                tripsplit = splitmsg[1].split('-')
            else:
                raise ValueError("Trip argument not recognized. Make sure it is in the format XXX-YYY.")
            if tripsplit[0] not in locations or tripsplit[1] not in locations:
                raise ValueError("Location code was not recognized, please try again.")
            self.return_ticket(tripsplit[0], tripsplit[1], splitmsg[2])
        elif splitmsg[0] == 'RETURNRT_TICKET':
            if len(splitmsg) < 3:
                raise ValueError("Missing argument, please try again.\n")
            if '-' in splitmsg[1]:
                tripsplit = splitmsg[1].split('-')
            else:
                raise ValueError("Trip argument not recognized. Make sure it is in the format XXX-YYY.")
            if tripsplit[0] not in locations or tripsplit[1] not in locations:
                raise ValueError("Location code was not recognized, please try again.")
            self.return_roundtrip_ticket(tripsplit[0], tripsplit[1], splitmsg[2])
        else:
            return 0

        return 1

    def print_flights(self):
        formattedString = ''
        sorted_flights = ''
        for (sk, dk), [v1, v2] in sorted(flights.items()):
            sorted_flights += '{0:3}-{1:3}    {2:^5}   ${3:^5}\n'.format(sk, dk, v1, v2)
        formattedString = column_titles + '\n' + sorted_flights

        self.csocket.sendall(bytes(str(formattedString),'UTF-8'))
        

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((socket.gethostbyname(HOST), PORT))
    
with open("flights.txt", "r") as readFile:
    lines = readFile.readlines()

for line in lines:
    line = line.strip()
    line = line.split(' ')
    tripsplit = line[0].split('-')
    if str(tripsplit[0]) not in locations:
        locations.add(tripsplit[0])
    if str(tripsplit[1]) not in locations:
        locations.add(tripsplit[1])
    flights[(tripsplit[0], tripsplit[1])] = [int(line[1]), int(line[2])]
    flights[(tripsplit[1], tripsplit[0])] = [int(line[1]), int(line[2])]

print("Server started")
print("Waiting for client request..")

while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()


