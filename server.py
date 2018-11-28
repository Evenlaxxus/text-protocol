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
# NIE       klient nie zgadł liczby
# END       wykorzystano wszystkie próby
# NXT       podaj kolejną liczbę
#########################################################

import socket
import sys
import datetime
import random
import math
import threading
import traceback

# import time
# import socketserver


def header_pack(key, value):
    return key + ">" + value + "<"


def header_unpack(header):
    devider = header.find(">")
    key = header[:devider]
    value = header[devider+1:len(header)-1]
    return [key, value]


def encapsulation(operation, answer, id, data):
    time = datetime.datetime.now().time().replace(microsecond=0)
    if data is None:
        data = ""
    return "[" + str(time) + "]" + "<" + header_pack("Operacja", operation) + header_pack("Odpowiedz", answer) + header_pack("Identyfikator", id) + header_pack("Dane", data)


def deencapsulation(recv_t):
    recv = str(recv_t[0])
    print("Gowno: " + recv)
    operation = recv[recv.find("<Operacja>") + 10: recv.find("<Odpowiedz>")]
    answer = recv[recv.find("<Odpowiedz>") + 11: recv.find("<Identyfikator>")]
    id = recv[recv.find("<Identyfikator>") + 15: recv.find("<Dane>")]
    data = recv[recv.find("<Dane>") + 6: len(recv) - 1]
    return {"Operacja": operation, "Odpowiedz": answer, "ID": id, "Dane": data}


def make_attempt(L1, L2):
    attempts = int(math.floor((L1 + L2) / 2))
    return attempts


def init_id():
    x = random.randint(100, 200)
    return [x, x+1]


def server_available(ids):
    if len(ids) == 0:
        return False
    else:
        return True


def receive_data():
    x = deencapsulation(sock.recvfrom(4096))
    if x:
        return x
    else:
        return None


def wait_for_conf():
    while True:
        if receive_data()["Operacja"] == "Conf":
            break


host = "127.0.0.1"
port = 27015
id_list = init_id()


def client_thread(ip, port):
    global id_list
    addr = (ip, port)
    if len(id_list) == 0:
        sock.sendto(encapsulation("Full", "", "", "").encode(encoding='UTF-8'), addr)
        print("Somebody tried to start session")
    else:
        is_active = True
        session_id = id_list.pop(0)
        numbers = []
        secret = 0
        attempts = 0
        sock.sendto(encapsulation("Hi", "", "", "").encode(encoding='UTF-8'), addr)
        while is_active:
            data = receive_data()
            if data:
                if data["Operacja"] == "ID":
                    sock.sendto(encapsulation("ID", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                    print("Sending ID [" + str(session_id) + "] to client" )
                    wait_for_conf()
                elif data["Operacja"] == "Num":
                    if len(numbers) == 0:
                        numbers[0] = int(data["Dane"])
                        sock.sendto(encapsulation("Con", "Next", session_id, ""), addr)
                        print("Cliet [" + "] sent first number: " + str(numbers[0]))
                        wait_for_conf()
                    elif len(numbers) == 1:
                        numbers[1] = int(data["Dane"])
                        attempts = make_attempt(numbers[0], numbers[1])
                        secret = random.randint(0, 255)
                        sock.sendto(encapsulation("Con", "OK", session_id, ""), addr)
                        print("Client [" + "] sent second number: " + str(numbers[1]))
                        print("Secret number is " + secret + ", number of attempts is " + attempts)
                        wait_for_conf()
                elif data["Operacja"] == "Try":
                    if int(data["Dane"] == secret):
                        sock.sendto(encapsulation("Ans", "TAK", session_id, "").encode(encoding='UTF-8'), addr)
                        print("Client guessed our secret")
                        wait_for_conf()
                    elif attempts == 0:
                        sock.sendto(encapsulation("Ans", "END", session_id, ""), addr)
                        print("Client guessed  has no attempts left")
                        wait_for_conf()
                    else:
                        sock.sendto(encapsulation("Ans", "NXT", session_id, ""), addr)
                        print("Client guessed wrong")
                        wait_for_conf()
                elif data["Operacja"] == "Bye":
                    sock.sendto(encapsulation("Bye", "", session_id, ""), addr)
                    print("Ending session")
                    is_active = False
                    id_list.append(str(session_id))


try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except:
    print("Socket not created. Error: " + str(sys.exc_info()))
    sys.exit()

try:
    sock.bind((host, port))
except:
    print("Bind failed. Error : " + str(sys.exc_info()))
    sys.exit()


while True:
    data1 = receive_data()
    # print("Message: ", data)
    try:
        if data1["Operacja"] == "Hi":
            client_thread(host, port)
    except:
        print("Thread did not start.")
        traceback.print_exc()


# class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
#
#     def handle(self):
#         data = self.request[0].strip()
#         socket = self.request[1]
#         current_thread = threading.current_thread()
#         print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))
#         socket.sendto(data.upper(), self.client_address)
#
#
# class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
#     pass
#
#
# if __name__ == "__main__":
#     HOST, PORT = "127.0.0.1", 27015
#
#     server = ThreadedUDPServer((HOST, PORT), ThreadedUDPRequestHandler)
#
#     server_thread = threading.Thread(target=server.serve_forever)
#     server_thread.daemon = True
#
#     try:
#         server_thread.start()
#         print("Server started at {} port {}".format(HOST, PORT))
#         while True: time.sleep(100)
#     except (KeyboardInterrupt, SystemExit):
#         server.shutdown()
#         server.server_close()
#         exit()