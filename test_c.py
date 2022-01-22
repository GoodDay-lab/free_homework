import time
import socket
import json


while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.0.100', 5555))
    response = json.loads(sock.recv(128))
    partSize = response['part_size']
    fileName = response['file_name']
    with open('{}'.format(fileName), 'wb') as file:
        for _ in range(response['parts']):
            data = sock.recv(partSize)
            file.write(data)
    break

