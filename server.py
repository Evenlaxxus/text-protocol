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

addr_c = None


def encapsulation(operation, answer, id, data):
    time = datetime.datetime.now().replace(microsecond=0)
    if data is None:
        return "Data" + ">" + str(time) + "<" + "Operacja" + ">" + operation + "<" + "Odpowiedz" + ">" + answer + "<" + "Identyfikator" + ">" + id
    else:
        return "Data" + ">" + str(time) + "<" + "Operacja" + ">" + operation + "<" + "Odpowiedz" + ">" + answer + "<" + "Identyfikator" + ">" + str(id) + "<" + "Dane" + ">" + data


def deencapsulation(recv_t):
    global addr_c
    recv = str(recv_t[0])
    addr_c = recv_t[1]
    print(recv)
    operation = recv[recv.find("<Operacja>") + 10: recv.find("<Odpowiedz>")]
    answer = recv[recv.find("<Odpowiedz>") + 11: recv.find("<Identyfikator>")]
    id = recv[recv.find("<Identyfikator>") + 15: recv.find("<Dane>")]
    data = recv[recv.find("<Dane>") + 6: len(recv) - 1]
    return {"Operacja": operation, "Odpowiedz": answer, "ID": id, "Dane": data}


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
        if receive_data()["Operacja"] == "Con":
            break


host = "127.0.0.1"
port = 27015
id_list = init_id()


def client_thread(ip, port):
    global id_list, addr_c

    if len(id_list) == 0:
        sock.sendto(encapsulation("Full", "", "", "").encode(encoding='UTF-8'), addr_c)
        print("Somebody tried to start session")
    else:
        is_active = True
        session_id = id_list.pop(0)
        numbers = []
        secret = 0
        attempts = 0
        sock.sendto(encapsulation("Con", "", "", "").encode(encoding='UTF-8'), addr_c)
        sock.sendto(encapsulation("Hi", "", "", "").encode(encoding='UTF-8'), addr_c)
        while is_active:
            data = receive_data()
            if data:
                if data["Operacja"] == "ID":
                    sock.sendto(encapsulation("Con", "", "", "").encode(encoding='UTF-8'), addr_c)
                    sock.sendto(encapsulation("ID", "", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                    print("Sending ID [" + str(session_id) + "] to client")
                    wait_for_conf()
                elif data["Operacja"] == "Num":
                    if len(numbers) == 0:
                        numbers.append(int(data["Dane"]))
                        print("Cliet [" + str(session_id) + "] sent first number: " + str(numbers[0]))
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                        sock.sendto(encapsulation("Num", "NXT", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                        wait_for_conf()
                    elif len(numbers) == 1:
                        numbers.append(int(data["Dane"]))
                        print("Client [" + str(session_id) + "] sent second number: " + str(numbers[1]))
                        attempts = int(math.floor((numbers[0] + numbers[1]) / 2))
                        secret = random.randint(0, 255)
                        print("Secret number is " + str(secret) + ", number of attempts is " + str(attempts))
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                        sock.sendto(encapsulation("Num", "", str(session_id), str(attempts)).encode(encoding='UTF-8'), addr_c)
                        wait_for_conf()
                elif data["Operacja"] == "Try":
                    if int(data["Dane"]) == secret:
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                        sock.sendto(encapsulation("Ans", "TAK", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                        print("Client guessed our secret")
                        wait_for_conf()
                    elif attempts == 0:
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                        sock.sendto(encapsulation("Ans", "END", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                        print("Client guessed  has no attempts left")
                        wait_for_conf()
                    else:
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                        sock.sendto(encapsulation("Ans", "NXT", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                        print("Client guessed wrong")
                        attempts = attempts -1
                        wait_for_conf()
                elif data["Operacja"] == "Bye":
                    sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr_c)
                    sock.sendto(encapsulation("Bye", "", str(session_id), "").encode(encoding='UTF-8'), addr_c)
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