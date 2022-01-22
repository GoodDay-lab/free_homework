import socket
import json


i = 0
while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.0.100', 5555))
    with open("homework.py", 'rb') as file:
        chunks = file.__sizeof__() // 2048 + bool(file.__sizeof__() % 2048)
        byteReadSize = 2048
        request = {
            "action": "send_solution",
            "payload": {"file_name": 'homework.py',
                        "chunks": chunks,
                        "byte_read": byteReadSize}
        }
        sock.send(json.dumps(request).encode())
        print(sock.recv(128))
        for _ in range(chunks):
            sock.send(file.read(byteReadSize))
    i += 1
    break

