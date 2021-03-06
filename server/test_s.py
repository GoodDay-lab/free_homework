import json
import math
import random
import socket
import threading
import time
import os
from crypto import encode_, decode_, create_secure_key

with open('./settings.json') as file:
    personal_data = json.load(file)
    AUTH_KEY = personal_data['password']
    USERS_ONLINE = personal_data['users_online']

HOST = '0.0.0.0'
PORT = 5555
QUERY = []
THREADS = [] * 10

CHUNK_SIZE = 2048
CHUNKS_LIMIT = 1024 * 7.5

MAIN_THREAD = threading.main_thread()

# STATUSES
OK = 200
FILE_NOT_FOUND = 401
ABNORMAL_FILE_EXTENSION = 402
ABNORMAL_FILE_SIZE = 403
ABNORMAL_AUTH_KEY = 404

# EXTENSIONS
NORMAL_FILE_EXTENSIONS = ['.txt', '.py', '.pdf', '.png', '.jpg']


def check_auth_key(client, request):
    if request['auth_key'] == AUTH_KEY:
        return True
    send_data(client, ABNORMAL_AUTH_KEY, {"Error": "YOU USES WRONG AUTH KEY"})
    client.close()
    return False


def send_data(client, status, data):
    message = {
        "status": status,
        "data": data,
        "time": time.time()
    }
    client.send(json.dumps(message).encode())


def get_solution(client, data):
    fileName = os.path.join('.', 'data', data['payload'])
    if not os.path.isfile(fileName):
        send_data(client, FILE_NOT_FOUND, {"Error": "NO SOLUTION FOUND"})
        return

    with open(fileName, 'rb') as file:
        chunks = math.ceil(os.path.getsize(fileName) / CHUNK_SIZE)
        secure_key = create_secure_key()
        send_data(client, OK, {"file_name": data["payload"], "chunks": chunks,
                               "chunk_size": CHUNK_SIZE, "secure_key": secure_key})
        for _ in range(chunks):
            chunk = file.read(CHUNK_SIZE)
            client.send(encode_(chunk, secure_key))
            time.sleep(0.001)
    client.close()


def send_solution(client, data):
    fileName = data['payload']['file_name']
    chunks = data['payload']['chunks']
    chunkSize = data['payload']['chunk_size']
    secure_key = data['payload']['secure_key']

    fileName = os.path.join('.', 'data', os.path.split(fileName)[-1])
    name, ext = os.path.splitext(fileName)

    if ext not in NORMAL_FILE_EXTENSIONS:
        send_data(client, ABNORMAL_FILE_EXTENSION, {'Error': "FILE EXTENSION IS NOT VALID"})
        return
    if chunks > CHUNKS_LIMIT:
        send_data(client, ABNORMAL_FILE_SIZE, {'Error': "FILE SIZE TOO MUCH"})
        return

    count = 1
    while os.path.exists(name + str(count) + ext):
        count += 1

    fileName = name + str(count) + ext
    with open(fileName, 'wb') as file, open('temp.py', 'wb') as file_temp:
        send_data(client, OK, {'file_name': fileName})
        for _ in range(chunks):
            chunk = client.recv(chunkSize)
            file.write(decode_(chunk, secure_key))
            file_temp.write(chunk)
    client.close()


def get_filenames(client, data):
    dirName = os.path.join('.', 'data')
    extension = data['payload']
    allFiles = []

    for _, a, files in os.walk(dirName):
        allFiles = files

    allFiles = list(filter(lambda filename: os.path.splitext(filename)[-1] == extension or extension == '*', allFiles))
    allFiles = list(map(lambda filename: (filename, os.path.getsize('./data/' + filename)), allFiles))
    response = {
        'files': allFiles
    }
    send_data(client, OK, response)
    client.close()


def terminate_server(client, data):
    password = data['payload']
    client.close()
    if password == 'Jinja':
        pass


FUNCTIONALITY = {"get_solution": get_solution,
                 "send_solution": send_solution,
                 "get_filenames": get_filenames,
                 "terminate_server": terminate_server}


def coroutine():
    global THREADS, QUERY, FUNCTIONALITY
    while True:
        client, data = (yield)
        QUERY.insert(0, (client, data))

        if True:
            qclient, qdata = QUERY.pop(-1)
            thread = threading.Thread(target=FUNCTIONALITY[f"{qdata['action']}"], args=(qclient, qdata))
            thread.start()
            THREADS.append(thread)


def clean_threads_coroutine():
    global THREADS
    index = 0
    while True:
        if len(THREADS) > 0:
            index %= len(THREADS)
            if not THREADS[index].is_alive():
                THREADS.pop(index)
            index += 1
        yield


def main(host, tcp_port):
    threads_cleaner = clean_threads_coroutine()
    tasks_manager = coroutine()
    next(tasks_manager)
    tcp_listener = TcpListener(host, tcp_port, tasks_manager, threads_cleaner)
    tcp_listener.start()

    is_running = True
    while is_running:
        try:
            cmd = input('admin@admin $ ')
        except KeyboardInterrupt:
            is_running = False
            continue
        if cmd == 'quit':
            is_running = False
    tcp_listener.stop()
    tcp_listener.join()


class TcpListener(threading.Thread):
    def __init__(self, host, port, tasks_query, cleaner):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.is_running = True
        self.tasks_query = tasks_query
        self.cleaner = cleaner
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.serv_sock.settimeout(1)
        self.serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_sock.setblocking(True)
        self.serv_sock.settimeout(1)
        self.serv_sock.bind((self.host, self.port))
        self.serv_sock.listen(USERS_ONLINE)

        while self.is_running:
            next(self.cleaner)
            try:
                client, addr = self.serv_sock.accept()
            except socket.timeout:
                continue
            print('[i] Connected to server {}:{}'.format(*addr))

            try:
                time.sleep(0.001)
                data = json.loads(client.recv(1024))
                if check_auth_key(client, data):
                    self.tasks_query.send((client, data))
            except (json.decoder.JSONDecodeError, ConnectionResetError):
                pass
        self.serv_sock.close()

    def stop(self):
        self.is_running = False


if __name__ == '__main__':
    main(HOST, PORT)
