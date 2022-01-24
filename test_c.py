import os.path
import socket
import json
import sys
import math
from crypto import encode, decode, create_secure_key

with open('settings.json') as file:
    data = json.load(file)
    SERVER_HOST = data['HOST']
    SERVER_PORT = data['PORT']
    AUTH_KEY = data['AUTH_KEY']

SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)
OK = 200
CHUNK_SIZE = 2048
RESPONSE_SIZE = 1024
logging = True


def get_chunks(file):
    return math.ceil(os.path.getsize(file) / CHUNK_SIZE)


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
        chunks = get_chunks(fileName)
        print(chunks)
        secure_key = create_secure_key()
        request = {
            "auth_key": AUTH_KEY,
            "action": "send_solution",
            "payload": {
                "file_name": fileName,
                "chunks": chunks,
                "chunk_size": CHUNK_SIZE,
                "secure_key": secure_key
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
            sock.send(encode(chunk, secure_key))


def get_solution(fileName):
    """ fileName is a name of file on server, you can use func get_filenames() to get them """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS)
    request = {
        "auth_key": AUTH_KEY,
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
    secure_key = response['secure_key']

    with open(downloadedFileName, 'wb') as file:
        for _ in range(chunks):
            file.write(decode(sock.recv(chunkSize), secure_key))


def get_filenames(extension="*"):
    """ Default extension is '*' that means you'll get a list of all files """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS)
    request = {
        "auth_key": AUTH_KEY,
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
        "auth_key": AUTH_KEY,
        'action': 'terminate_server',
        'payload': password
    }
    sock.send(json.dumps(request).encode())
