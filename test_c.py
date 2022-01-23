import os.path
import socket
import json
import sys


SERVER_HOST = '192.168.0.102'
SERVER_PORT = 5555
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)
OK = 200
CHUNK_SIZE = 2048
RESPONSE_SIZE = 1024

get_chunks = lambda file_obj: file_obj.__sizeof__() // 2048 + bool(file_obj.__sizeof__() % 2048)


def parse_response(response):
    if response["status"] == OK:
        sys.stdout.write('STATUS: {}\r\nDATA: {}\r\n'.format(response['status'], response['data']))
        return response["data"]
    else:
        sys.stderr.write('STATUS: {}\r\nEXCEPTION: {}\r\n'.format(response['status'], response['data']['Error']))
        raise RuntimeError


def send_solution(fileName):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS)
    if not os.path.exists(fileName):
        return False
    with open(fileName, 'rb') as file:
        chunks = get_chunks(file)
        request = {
            "action": "send_solution",
            "payload": {
                "file_name": fileName,
                "chunks": chunks,
                "chunk_size": CHUNK_SIZE
            }
        }
        sock.send(json.dumps(request).encode())
        raw_response = json.loads(sock.recv(RESPONSE_SIZE))
        try:
            response = parse_response(raw_response)
        except RuntimeError:
            return
        for _ in range(chunks):
            chunk = file.read(CHUNK_SIZE)
            sock.send(chunk)


def get_solution(fileName):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS)
    request = {
        "action": "get_solution",
        "payload": fileName
    }
    sock.send(json.dumps(request).encode())
    raw_response = json.loads(sock.recv(RESPONSE_SIZE))
    try:
        response = parse_response(raw_response)
    except RuntimeError:
        return
    downloadedFileName = response['file_name']
    chunks = response['chunks']
    chunkSize = response['chunk_size']

    with open(downloadedFileName, 'wb') as file:
        for _ in range(chunks):
            file.write(sock.recv(chunkSize))


def get_filenames(extenstion="*"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS)
    request = {
        "action": "get_filenames",
        "payload": extenstion
    }
    sock.send(json.dumps(request).encode())
    raw_response = json.loads(sock.recv(RESPONSE_SIZE))
    try:
        response = parse_response(raw_response)
    except RuntimeError:
        return
    return response['files']


while True:
    get_filenames()
    get_solution('python.jpg')
    break


