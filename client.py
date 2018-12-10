import socket
import datetime
import time
from threading import Timer


# pakowanie danych
def encapsulation(operation, answer, id, data):
    time = datetime.datetime.now().replace(microsecond=0)
    if data =="":
        return "Data" + ">" +  str(time) + "<" + "Operacja" + ">" + operation + "<" + "Odpowiedz" + ">" + answer + "<" + "Identyfikator" + ">" + id+"<"
    else:
        return "Data" + ">" +  str(time) + "<" + "Operacja" + ">" + operation + "<" + "Odpowiedz" + ">" + answer + "<" + "Identyfikator" + ">" + id + "<" + "Dane" + ">" + data+"<"

    
# rozpakowywanie danych
def deencapsulation(recv_t):
    global addr_c
    recv = str(recv_t[0])
    operation = recv[recv.find("<Operacja>") + 10: recv.find("<Odpowiedz>")]
    answer = recv[recv.find("<Odpowiedz>") + 11: recv.find("<Identyfikator>")]
    if recv.find("<Dane>")==-1:
        id = recv[recv.find("<Identyfikator>") + 15: recv.rfind("<")]
    else:
        id = recv[recv.find("<Identyfikator>") + 15: recv.rfind("<Dane")]
    data = recv[recv.find("<Dane>") + 6: recv.rfind("<")] #to działa jak danych nie ma? jeszcze nie wiem
    return {"Operacja": operation, "Odpowiedz": answer, "ID": id, "Dane": data}


# otrzymywanie danych
def receive_data():
    x = deencapsulation(sock.recvfrom(4096))
    if x:
        return x
    else:
        return None


# domyślny adres serwera i port
host = "127.0.0.1"
port = 27015
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
time_exceeded=False


def timeout():
    global time_exceeded
    print("CONNECTION TIMEOUT, DISCONNECTING")
    sock.sendto(encapsulation("Bye", "", "", "").encode(encoding='UTF-8'), (host, port))
    time_exceeded = True


# oczekiwanie na potwierdzenie pakietu
def wait_for_conf():
    t = Timer(8, timeout)
    t.start()
    print("Waiting for connection")
    while True:
        if receive_data()["Operacja"] == "Con":
            t.cancel()
            break

            
def main():
    global time_exceeded
    session_id = ""
    attempts = 0


    a=str(input("Enter ip:"))
    if a!="":
        host=a
    print("IP: ", host)
    print("Port: ", port)

    serverAdressPort = (host, port)


    message = encapsulation("Hi", "", "", "")
    sock.sendto(message.encode(encoding='UTF-8'), (host, port))

    wait_for_conf()

    while not time_exceeded:
        while True:
            data = receive_data()
            if data["Operacja"] == "Hi":
                print("Server responded with \"Hi\". Asking for ID")
                sock.sendto(encapsulation("Con", "", "", "").encode(encoding='UTF-8'), serverAdressPort)
                sock.sendto(encapsulation("ID", "", "", "").encode(encoding='UTF-8'), serverAdressPort)
                wait_for_conf()
            if data["Operacja"] == "Full":
                print("Server is full.")
                sock.sendto(encapsulation("Con", "", "", "").encode(encoding='UTF-8'), serverAdressPort)
                sock.sendto(encapsulation("Bye", "", "", "").encode(encoding='UTF-8'), serverAdressPort)
                break
            if data["Operacja"] == "ID":
                print("Server assigned me ID:" + data["ID"])
                session_id = data["ID"]
                a = input("Enter first even number:")
                while a.isdigit() is False or (a.isdigit() is True and int(a) % 2 != 0):  # naturalne z zerem?
                    a = input('Enter an EVEN NUMBER: ')
                sock.sendto(encapsulation("Con", "", session_id, "").encode(encoding='UTF-8'), serverAdressPort)
                sock.sendto(encapsulation("Num", "", session_id, str(a)).encode(encoding='UTF-8'), serverAdressPort)
                wait_for_conf()
            if data["Operacja"] == "Num" and data["Odpowiedz"] == "NXT":
                a = input("Enter second even number: ")
                while a.isdigit() is False or (a.isdigit() is True and int(a) % 2 != 0):  # naturalne z zerem?
                    a = input('Enter an EVEN NUMBER: ')
                sock.sendto(encapsulation("Con", "", session_id, "").encode(encoding='UTF-8'), serverAdressPort)
                sock.sendto(encapsulation("Num", "", session_id, str(a)).encode(encoding='UTF-8'), serverAdressPort)
                wait_for_conf()
            if data["Operacja"] == "Num" and data["Odpowiedz"] != "NXT":
                attempts = int(data["Dane"])
                print("Server is ready to play. You have " + str(attempts) + " tries.")
                guess = input("Enter number between 0-1000: ")
                while guess.isdigit() is False or (guess.isdigit() is True and 1000 < int(guess) < -1):  # naturalne z zerem?
                    guess = input('Try again: ')
                sock.sendto(encapsulation("Con", "", session_id, "").encode(encoding='UTF-8'), serverAdressPort)
                sock.sendto(encapsulation("Try", "", session_id, str(guess)).encode(encoding='UTF-8'), serverAdressPort)
                wait_for_conf()
            if data["Operacja"] == "Ans" and data["Odpowiedz"] == "TAK":
                print("That's right, you guessed!")
                sock.sendto(encapsulation("Con", "", session_id, "").encode(encoding='UTF-8'), serverAdressPort)
                print("Disconnecting from a server.")
                sock.sendto(encapsulation("Bye", "", session_id, "").encode(encoding='UTF-8'), serverAdressPort)
                wait_for_conf()
            if data["Operacja"] == "Ans" and data["Odpowiedz"] == "END":
                print("You ran out of tries.")
                sock.sendto(encapsulation("Con", "", session_id, "").encode(encoding='UTF-8'), serverAdressPort)
                sock.sendto(encapsulation("Bye", "", session_id, "").encode(encoding='UTF-8'), serverAdressPort)
                wait_for_conf()
            if data["Operacja"] == "Ans" and data["Odpowiedz"] == "NXT":
                attempts = attempts - 1
                print("You missed. Tries left: " + str(attempts) + ".")

                guess = input("Enter number between 0-1000: ")
                while guess.isdigit() is False or (guess.isdigit() is True and 1000 < int(guess) < -1):  # naturalne z zerem?
                    guess = input('Try again: ')
                sock.sendto(encapsulation("Con", "", session_id, "").encode(encoding='UTF-8'), serverAdressPort)
                sock.sendto(encapsulation("Try", "", session_id, str(guess)).encode(encoding='UTF-8'), serverAdressPort)
                wait_for_conf()
            if data["Operacja"] == "Bye":
                time_exceeded = True
                break
    sock.close()
    print("PROGRAM END")




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sock.sendto(encapsulation("Bye", "", "", "").encode(encoding='UTF-8'), (host,port))
        sock.close()
