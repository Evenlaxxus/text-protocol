#########################################################
# TODO serwer wielowątkowy
# TODO potwierdzenia odbioeu pakietów
# TODO jak ograniczyć to do dwóch klientów??????? (lista dwuelementowa z ID)
#########################################################
#                     OPERACJE
# Hi        Nawiązanie połączenia
# ID        żądanie i otrzymanie ID
# Full      serwer zajęty
# Num       podanie liczby
# Try       zgadywanie liczby przez klienta
# Con       potwierdzenie otrzymania pakietu
# Ans       odpowiedź serwera
# Bye       zakończenie sesji i zwrócenie ID
#########################################################
#                     Odpowiedzi serwera
# TAK       klient zgadł liczbę
# END       wykorzystano wszystkie próby
# NXT       podaj kolejną liczbę
#########################################################
## TRY,RDY-> serwer gotów do zgadywanka

import socketserver
import threading
import random
import datetime
import math

#string do wysłania
def encapsulation(operation, answer, id, data):
    time = datetime.datetime.now().time().replace(microsecond=0)
    if data is None:
        data = ""
    return "[" + str(time) + "]" + "Operacja>" + operation + "<" + "Odpowiedz>" + answer + "<" +"Identyfikator>"+id+"<" + "Dane>"+ data+"<"

def deencapsulation(datagram_):
    datagram=str(datagram_)
    operation = datagram[datagram.find("Operacja>") + 9:datagram.find("<Odpowiedz>")]
    answer = datagram[datagram.find("<Odpowiedz>") + 11:datagram.find("<Identyfikator>")]
    id = datagram[datagram.find("<Identyfikator>") + 15:datagram.find("<Dane>")]
    data = datagram[datagram.find("<Dane>") + 6:len(datagram) - 1]
    #print(operation + " " + answer) to potrzebne?

    return {"Operacja": operation, "Odpowiedz": answer, "ID": id, "Dane": data}

def make_attempt(L1, L2):
    attempts = int(math.floor((L1 + L2) / 2))
    return attempts

def init_id():
    x = random.randint(100, 200)
    return [x, x + 1]

# Create a tuple with IP Address and Port Number
ServerAddress = ("127.0.0.1", 8888)


id_list = init_id()
#do wysyłania trzeba enkodować, przy odbiorze chyba nie
# odbierz dane-> data=deencapsulation(self.rfile.readline().strip())
# wyslij dane-> self.wfile.write(encapsulation(OP,RESP,ID,DATA).encode(encoding='UTF-8'))

# Subclass the DatagramRequestHandler
class MyUDPRequestHandler(socketserver.DatagramRequestHandler):
    # Override the handle() method
    def handle(self):
        global id_list
        is_active = True
        no_ack = True
        session_id = id_list.pop(0)
        numbers = []
        secret = 0
        attempts = 0
        data=deencapsulation(self.rfile.readline().strip())
        if data["Operacja"] == "Hi":
            if len(id_list) == 0:
                self.wfile.write(encapsulation("Con","","","").encode(encoding='UTF-8'))
                self.wfile.write(encapsulation("Full","","","").encode(encoding='UTF-8'))
                print("Somebody tried to start session")
            else:
                self.wfile.write(encapsulation("Con", "", "", "").encode(encoding='UTF-8'))
                self.wfile.write(encapsulation("Hi", "", "", "").encode(encoding='UTF-8'))
                print("Guest connected.")
        while is_active:
            while no_ack:
                data = deencapsulation(self.rfile.readline().strip())
                if data["Operacja"] == "Con":
                    no_ack = False
        data = deencapsulation(self.rfile.readline().strip())
        if data["Operacja"] == "ID":
            self.wfile.write(encapsulation("ID", "", str(session_id), "").encode(encoding='UTF-8'))
            print("Sending ID [" + str(session_id) + "] to client")
        elif data["Operacja"] == "Num":
            if len(numbers) == 0:
                numbers[0] = int(data["Dane"])
                self.wfile.write(encapsulation("Con", "NXT", str(session_id), "").encode(encoding='UTF-8'))
                print("Client [" +str(session_id)+ "] sent first number: " + str(numbers[0]))
            elif len(numbers) == 1:
                numbers[1] = int(data["Dane"])
                attempts = make_attempt(numbers[0], numbers[1])
                secret = random.randint(0, 255)
                self.wfile.write(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8')) #todo-> rafał sprawdź, bo mi to ok tu nie pasuje
                self.wfile.write(encapsulation("Try", "RDY", str(session_id), "").encode(encoding='UTF-8'))
                print("Client ["+str(session_id)+"] sent second number: " + str(numbers[1]))
                print("Secret number is " + str(secret) + ", number of attempts is " + str(attempts))
                print("Server is ready for a game.")
                #server ready for guessing
        elif data["Operacja"] == "Try":
            if int(data["Dane"] == secret):
                self.wfile.write(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'))
                self.wfile.write(encapsulation("Ans", "TAK", str(session_id), "").encode(encoding='UTF-8'))
                print("Client guessed our secret number")
            elif attempts == 0:
                self.wfile.write(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'))
                self.wfile.write(encapsulation("Ans", "END", str(session_id), "").encode(encoding='UTF-8'))
                print("Client guessed  has no attempts left")
            else:
                self.wfile.write(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'))
                self.wfile.write(encapsulation("Ans", "NXT", str(session_id), "").encode(encoding='UTF-8'))
                attempts=attempts-1
                print("Client guessed wrong")

        elif data["Operacja"] == "Bye":
            self.wfile.write(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'))
            self.wfile.write(encapsulation("Bye", "", str(session_id), "").encode(encoding='UTF-8'))
            print("Ending session")
            is_active = False
            id_list.append(session_id)
        #nie wiem jak zamknąć XD



# Create a Server Instance

UDPServerObject = socketserver.ThreadingUDPServer(ServerAddress, MyUDPRequestHandler)

# Make the server wait forever serving connections

UDPServerObject.serve_forever()


## obsluga protokolu:
# ->sprawdzenie, czy jest tylko dwóch, jak trzeci to nara (wyślij 'nara')
# ->jak się mieści w przedziale to odsyłam 'hi'
# ->id
# ->numery dwa
# ->zgaduj liczbę, odliczaj ilość prób
# ->
#
#
#
#
#
##
