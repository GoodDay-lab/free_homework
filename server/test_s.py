import json
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 5555))
sock.listen(1)
PART_SIZE = 2048

while True:
    client_sock, address = sock.accept()

    with open('heloo.txt', 'rb') as file:
        parts = file.__sizeof__() // PART_SIZE + bool(file.__sizeof__() % PART_SIZE)
        print(parts)
        client_sock.send(json.dumps({"parts": parts, "part_size": PART_SIZE, "file_name": "heloo.txt"}).encode())
        for _ in range(parts):
            buffer = file.read(PART_SIZE)
            client_sock.send(buffer)
        client_sock.close()

