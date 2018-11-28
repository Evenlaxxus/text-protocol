import socket
import datetime


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


host = "127.0.0.1"
port = 27015
session = True

print("IP: ", host)
print("Port: ", port)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = encapsulation("Hi", "", "", "")

sock.sendto(message.encode(encoding='UTF-8'), (host, port))

# message = encapsulation("ID", "", "", "")
#
# sock.sendto(message.encode(encoding='UTF-8'), (host, port))

# data = sock.recvfrom(4096)
# print(data)

sock.close()
