import os.path
import socket
import json
import sys
import math

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)
OK = 200
CHUNK_SIZE = 2048
RESPONSE_SIZE = 1024
logging = True


def get_chunks(file_obj):
    return math.ceil(file_obj.__sizeof__() / CHUNK_SIZE)


def parse_response(response):
    if response["status"] == OK:
        if logging:
            sys.stdout.write('STATUS: {}\r\nDATA: {}\r\n'.format(response['status'], response['data']))
        return response["data"]
    else:
        if logging:
            sys.stderr.write('STATUS: {}\r\nEXCEPTION: {}\r\n'.format(response['status'], response['data']['Error']))
        raise RuntimeError


def send_solution(fileName):
    """ fileName probably may be a path """
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
    """ fileName is a name of file on server, you can use func get_filenames() to get them """
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


def get_filenames(extension="*"):
    """ Default extension is '*' that means you'll get a list of all files """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS)
    request = {
        "action": "get_filenames",
        "payload": extension
    }
    sock.send(json.dumps(request).encode())
    raw_response = json.loads(sock.recv(RESPONSE_SIZE))
    try:
        response = parse_response(raw_response)
    except RuntimeError:
        return
    return response['files']


def terminate_server(password):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS)
    request = {
        'action': 'terminate_server',
        'payload': password
    }
    sock.send(json.dumps(request).encode())


while True:
    get_filenames()
    break
