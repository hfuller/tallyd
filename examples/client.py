import codecs
import socket
s = socket.socket()
s.connect(("localhost", 5763))

while True:
    print(codecs.encode(s.recv(1024), "hex"))
