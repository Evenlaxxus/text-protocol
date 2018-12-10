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
#        C       S       C
#    Hi->        |      <-Hi
#              / | \
#       <-Con |  |  | Con->
#        <-Hi |  |  | Hi->
# thread sleep|  |  | thread sleeps
#
#               .
#               .
#               .
# -------------------------------------
# C1            MT           C2
# Info->        |
#             Info od C1?
#             Y: Info->CL1_comqu, wake up thread 1
#                N:
#             Info od C2?
#               Y:Info->Cl2_comqu, wake up thread 2
#               N:
#             Unknown client, send "FULL"
#
#########################################################

import socket
from threading import Event, Thread, Lock
import sys
import datetime
import queue
import random
import math
import time
from timeit import default_timer as timer

# eventy do zatrzymywania wątku
ev1 = Event()
ev2 = Event()
# kolejki do przechowywania komunikatów
CL1_comqu = queue.Queue(maxsize=3)
CL2_comqu = queue.Queue(maxsize=3)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
Comlist = [CL1_comqu, CL2_comqu]
evlist = [ev1, ev2]
cli_addr_list = [tuple(), tuple()]


def init_id():
    x = random.randint(100, 200)
    return [x, x + 1]


id_list = init_id()


def is_empty(any_structure):
    if any_structure:
        # print('Structure is not empty.')
        return False
    else:
        # print('Structure is empty.')
        return True


# w razie wu to
# utc_timestamp=datetime.datetime.utcnow().timestamp()
#
# from datetime import timezone
# dt = datetime(2015, 10, 19)
# timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
# print(timestamp)

def encapsulation(operation, answer, id, data):
    time = datetime.datetime.now().replace(microsecond=0)

    if data == "":
        return "Data" + ">" + str(
            time) + "<" + "Operacja" + ">" + operation + "<" + "Odpowiedz" + ">" + answer + "<" + "Identyfikator" + ">" + id + "<"
    else:
        return "Data" + ">" + str(
            time) + "<" + "Operacja" + ">" + operation + "<" + "Odpowiedz" + ">" + answer + "<" + "Identyfikator" + ">" + id + "<" + "Dane" + ">" + data + "<"


def deencapsulation(recv_t):
    global addr_c
    recv = str(recv_t[0])
    operation = recv[recv.find("<Operacja>") + 10: recv.find("<Odpowiedz>")]
    answer = recv[recv.find("<Odpowiedz>") + 11: recv.find("<Identyfikator>")]
    if recv.find("<Dane>") == -1:
        id = recv[recv.find("<Identyfikator>") + 15: recv.rfind("<")]
    else:
        id = recv[recv.find("<Identyfikator>") + 15: recv.rfind("<Dane")]
    data = recv[recv.find("<Dane>") + 6: recv.rfind("<")]  # to działa jak danych nie ma? jeszcze nie wiem
    return {"Operacja": operation, "Odpowiedz": answer, "ID": id, "Dane": data}


def wipe(id):
    global cli_addr_list
    a = tuple()
    cli_addr_list[id] = a


def clienthread(addr, ThID, session_id):
    global id_list, cli_addr_list
    sock.sendto(encapsulation("Con", "", "", "").encode(encoding='UTF-8'), addr)
    sock.sendto(encapsulation("Hi", "", "", "").encode(encoding='UTF-8'), addr)
    numbers = []
    secret = 0
    attempts = 0
    connection = True
    evlist[ThID].wait()  # tutaj jest wait
    while connection:
        while not Comlist[ThID].empty():
            x = Comlist[ThID].get()
            if x["Operacja"] == "Con":
                print("[" + str(session_id) + "] Data confirmed.")
                x = Comlist[ThID].get()
                if x["Operacja"] == "ID":
                    sock.sendto(encapsulation("Con", "", "", "").encode(encoding='UTF-8'), addr)
                    datax = encapsulation("ID", "", str(session_id), "")
                    sock.sendto(datax.encode(encoding='UTF-8'), addr)
                    print("[" + str(session_id) + "] Sending ID [" + str(session_id) + "] to client")
                elif x["Operacja"] == "Num":
                    if len(numbers) == 0:
                        numbers.append(int(x["Dane"]))
                        print("[" + str(x["ID"]) + "] Client sent first number: " + str(numbers[0]))
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                        sock.sendto(encapsulation("Num", "NXT", str(session_id), "").encode(encoding='UTF-8'), addr)
                    elif len(numbers) == 1:
                        numbers.append(int(x["Dane"]))
                        print("[" + str(session_id) + "] Client sent second number: " + str(numbers[1]))
                        attempts = int(math.floor((numbers[0] + numbers[1]) / 2))
                        secret = random.randint(0, 1000)
                        print("[" + str(session_id) + "] Secret number is " + str(
                            secret) + ", number of attempts is " + str(attempts))
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                        sock.sendto(encapsulation("Num", "", str(session_id), str(attempts)).encode(encoding='UTF-8'),
                                    addr)
                elif x["Operacja"] == "Try":
                    if int(x["Dane"]) == secret:
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                        sock.sendto(encapsulation("Ans", "TAK", str(session_id), "").encode(encoding='UTF-8'), addr)
                        print("[" + str(session_id) + "] Client guessed our secret")
                    elif attempts == 1:  # bo zero też liczył,
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                        sock.sendto(encapsulation("Ans", "END", str(session_id), "").encode(encoding='UTF-8'), addr)
                        print("[" + str(session_id) + "] Client has no attempts left")
                    else:
                        sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                        sock.sendto(encapsulation("Ans", "NXT", str(session_id), "").encode(encoding='UTF-8'), addr)
                        print("[" + str(session_id) + "] Client guessed wrong")
                        attempts = attempts - 1
                elif x["Operacja"] == "Bye":
                    sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                    sock.sendto(encapsulation("Bye", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                    print("Ending session")
                    connection = False
                    id_list.append(str(session_id))
                    wipe(ThID)
            elif x["Operacja"] == "Bye":
                sock.sendto(encapsulation("Con", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                sock.sendto(encapsulation("Bye", "", str(session_id), "").encode(encoding='UTF-8'), addr)
                print("[" + str(session_id) + "] Ending session")
                connection = False
                id_list.append(str(session_id))
                wipe(ThID)
            else:
                print("ERR, no con")
        evlist[ThID].clear()

    # czekaj aż event ci powie, że możesz pracować dalej
    # jak event ci powie, że możesz dalej pracować, to weź locka od maina
    # przeparsuj co tam w tym kontenerze
    # powrót do eventowego czekania


def mainthread(sock):
    global Comlist, id_list
    print("Main thread start.")
    while True:
        x = sock.recvfrom(8192)  # w najgorszym wypadku w buforze będzie con+coś z dwóch
        data1 = deencapsulation(x)
        if data1["Operacja"] == "Hi":
            if is_empty(cli_addr_list[0]) and is_empty(cli_addr_list[1]):
                cli_addr_list[0] = x[1]

                Thread(target=clienthread, args=(cli_addr_list[0], 0, id_list.pop(0))).start()
            elif is_empty(cli_addr_list[0]) == False and is_empty(cli_addr_list[1]):
                cli_addr_list[1] = x[1]
                Thread(target=clienthread, args=(cli_addr_list[1], 1, id_list.pop(0))).start()
            else:  # both taken
                print("Someone tried to connect, all seats taken.")
                sock.sendto(encapsulation("Con", "", "", "").encode(encoding='UTF-8'), x[1])
                sock.sendto(encapsulation("Full", "", "", "").encode(encoding='UTF-8'), x[1])
        else:
            if x[1] == cli_addr_list[0]:
                Comlist[0].put(data1)
                evlist[0].set()
            elif x[1] == cli_addr_list[1]:
                Comlist[1].put(data1)
                evlist[1].set()


def main():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 27015

    try:
        sock.bind((UDP_IP, UDP_PORT))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    Thread(target=mainthread, args=(sock,)).start()


if __name__ == "__main__":
    main()
