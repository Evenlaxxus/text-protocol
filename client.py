import socket
import datetime


def encapsulation(operation, answer, id, data):
    time = datetime.datetime.now().time().replace(microsecond=0)
    if data is None:
        data = ""
    return "[" + str(
        time) + "]" + "Operacja>" + operation + "<" + "Odpowiedz>" + answer + "<" + "Identyfikator>" + id + "<" + "Dane>" + data + "<"


def deencapsulation(datagram_):
    print("cojeskuwa")
    print(datagram_[0])
    datagram = str(datagram_[0])
    operation = datagram[datagram.find("Operacja>") + 9:datagram.find("<Odpowiedz>")]
    answer = datagram[datagram.find("<Odpowiedz>") + 11:datagram.find("<Identyfikator>")]
    id = datagram[datagram.find("<Identyfikator>") + 15:datagram.find("<Dane>")]
    data = datagram[datagram.find("<Dane>") + 6:len(datagram) - 1]
    # print(operation + " " + answer) to potrzebne?

    return {"Operacja": operation, "Odpowiedz": answer, "ID": id, "Dane": data}


host = "127.0.0.1"
port = 8888
bufferSize=2048
session = True

serverAdressPort=(host,port)
print("IP: ", host)
print("Port: ", port)

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
my_id=000
tries=0
connection_established=True
con_received=False
sock.sendto(encapsulation   ("Hi","","","").encode(encoding='UTF-8'),serverAdressPort)
MFS=sock.recvfrom(bufferSize)
print(MFS[0])
while connection_established:
    print ("linia 40")
    while not con_received:
        print ("linia 42")
        MFS=deencapsulation(sock.recvfrom(bufferSize))
        print("linia46")
        print(MFS)
        print("linia45")
        if MFS["Operacja"]=="Con":
            print("linia49")
            con_received=True
    MFS=deencapsulation(sock.recvfrom(bufferSize))
    if MFS["Operacja"]=="Hi":
        print("Server responded with \"Hi\". Asking for ID")
        sock.sendto(encapsulation("Con","","","").encode(encoding='UTF-8'),serverAdressPort)
        sock.sendto(encapsulation("ID","","","").encode(encoding='UTF-8'),serverAdressPort)
    if MFS["Operacja"]=="Full":
        print("Server is full.")
        sock.sendto(encapsulation("Con","","","").encode(encoding='UTF-8'),serverAdressPort)
        sock.sendto(encapsulation("Bye","","","").encode(encoding='UTF-8'),serverAdressPort)
    if MFS["Operacja"]=="ID":
        print("Server assigned me ID:" + MFS["ID"])
        my_id=MFS["ID"]
        sock.sendto(encapsulation("Con","","","").encode(encoding='UTF-8'),serverAdressPort)
        a=input("Enter first even number:")
        while a.isdigit() == False or (a.isdigit() == True and int(a)%2==0): #naturalne z zerem?
            a = input('Enter an EVEN NUMBER: ')
        sock.sendto(encapsulation("Num","","",str(a)).encode(encoding='UTF-8'),serverAdressPort)
        MFS=deencapsulation(sock.recvfrom(bufferSize))
        if MFS["Operacja"]=="Con" and ["Odpowiedz"]=="NXT":
            a=input("Enter second even number: ")
            while a.isdigit() == False or (a.isdigit() == True and int(a) % 2 == 0):  # naturalne z zerem?
                a = input('Enter an EVEN NUMBER: ')
        sock.sendto(encapsulation("Num","",my_id,str(a)).encode(encoding='UTF-8'),serverAdressPort)
    if MFS["Operacja"]=="Try" and MFS["Odpowiedz"]=="RDY":
        tries=int(MFS["Data"])
        print("Server is ready to play. You have "+MFS["Data"]+" tries.")
        sock.sendto(encapsulation("Con", "", "", "").encode(encoding='UTF-8'), serverAdressPort)
        a = input("Enter number between 0-1000: ")
        while a.isdigit() == False or (a.isdigit() == True and 1000 > int(a) > -1):  # naturalne z zerem?
            a = input('Try again: ')
        sock.sendto(encapsulation("Try","",my_id,str(a)).encode(encoding='UTF-8'),serverAdressPort)
    if MFS["Operacja"]=="Ans" and "TAK":
        print("That's right, you guessed!")
        sock.sendto(encapsulation("Con", "", my_id, "").encode(encoding='UTF-8'), serverAdressPort)
        print("Disconnecting from a server.")
        sock.sendto(encapsulation("Bye", "", my_id, "").encode(encoding='UTF-8'), serverAdressPort)
    if MFS["Operacja"]=="Ans" and "END":
        print("You ran out of tries.")
        sock.sendto(encapsulation("Con", "", my_id, "").encode(encoding='UTF-8'), serverAdressPort)
        sock.sendto(encapsulation("Bye", "", my_id, "").encode(encoding='UTF-8'), serverAdressPort)
    if MFS["Operacja"]=="Ans" and "NXT":
        tries=tries-1
        print("You missed. Tries left: "+str(tries)+".")
        a = input("Enter number between 0-1000: ")
        while a.isdigit() == False or (a.isdigit() == True and 1000 > int(a) > -1):  # naturalne z zerem?
            a = input('Try again: ')
        sock.sendto(encapsulation("Con", "", my_id, "").encode(encoding='UTF-8'), serverAdressPort)
        sock.sendto(encapsulation("Try", "", my_id, str(a)).encode(encoding='UTF-8'), serverAdressPort)
    if MFS["Operacja"]=="Bye":
        connection_established=False

sock.close()

# sock.sendto(encapsulation(OP,ANS,ID,DATA).encode(encoding='UTF-8'),serverAdressPort)
#
# sock.sendto(message.encode(encoding='UTF-8'), serverAdressPort)
# msgFromeServer=sock.recvfrom(bufferSize)

# message = encapsulation("ID", "", "", "")
#
# sock.sendto(message.encode(encoding='UTF-8'), (host, port))

# data = sock.recvfrom(4096)
# print(data)

sock.close()
