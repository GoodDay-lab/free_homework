import json
import socket
import threading
import time
import os

HOST = '0.0.0.0'
PORT = 5555
QUERY = []
THREADS = [] * 10

CHUNK_SIZE = 2048

# STATUSES
OK = 200
FILE_NOT_FOUND = 401
ABNORMAL_FILE_EXTENSION = 402
ABNORMAL_FILE_SIZE = 403

# EXTENSIONS
NORMAL_FILE_EXTENSIONS = ['.txt', '.py', '.pdf', '.png', '.jpg']


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
        fileSize = file.__sizeof__()
        chunks = fileSize // CHUNK_SIZE + bool(fileSize % CHUNK_SIZE)
        send_data(client, OK, {"file_name": data["payload"], "chunks": chunks, "chunk_size": CHUNK_SIZE})
        for _ in range(chunks):
            chunk = file.read(CHUNK_SIZE)
            client.send(chunk)
            time.sleep(0.001)
    client.close()


def send_solution(client, data):
    fileName = data['payload']['file_name']
    chunks = data['payload']['chunks']
    byteReadSize = data['payload']['chunk_size']

    fileName = os.path.join('.', 'data', os.path.split(fileName)[-1])
    print(fileName)
    name, ext = os.path.splitext(fileName)

    if not ext in NORMAL_FILE_EXTENSIONS:
        send_data(client, ABNORMAL_FILE_EXTENSION, {'Error': "FILE EXTENSION IS NOT VALID"})
        return
    if chunks > 25:
        send_data(client, ABNORMAL_FILE_SIZE, {'Error': "FILE SIZE TOO MUCH"})
        return

    count = 1
    while os.path.exists(name + str(count) + ext):
        count += 1

    fileName = name + str(count) + ext
    with open(fileName, 'wb') as file:
        send_data(client, OK, {'file_name': fileName})
        for _ in range(chunks):
            chunk = client.recv(byteReadSize)
            file.write(chunk)
    client.close()


def get_filenames(client, data):
    dirName = os.path.join('.', 'data')
    extension = data['payload']
    allFiles = []

    for _, a, files in os.walk(dirName):
        allFiles = files

    allFiles = list(filter(lambda filename: os.path.splitext(filename)[-1] == extension or extension == '*', allFiles))
    print(allFiles)
    response = {
        'files': allFiles
    }
    send_data(client, OK, response)
    client.close()


FUNCTIONALITY = {"get_solution": get_solution,
                 "send_solution": send_solution,
                 "get_filenames": get_filenames}


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
            print(THREADS[index].is_alive())
            if not THREADS[index].is_alive():
                THREADS.pop(index)
                print(len(THREADS), 'количество')
            index += 1
        yield


def main(host, tcp_port):
    threads_cleaner = clean_threads_coroutine()
    tasks_manager = coroutine()
    next(tasks_manager)
    tcp_listener = TcpListener(host, tcp_port, tasks_manager, threads_cleaner)
    tcp_listener.run()

    is_running = True
    while is_running:
        input('admin@admin $ ')


class TcpListener(threading.Thread):
    def __init__(self, host, port, tasks_query, cleaner):
        super().__init__()
        self.host = host
        self.port = port
        self.is_running = True
        self.tasks_query = tasks_query
        self.cleaner = cleaner

    def run(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv_sock.settimeout(1)
        serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv_sock.setblocking(True)
        serv_sock.bind((self.host, self.port))
        serv_sock.listen(5)

        while self.is_running:
            next(self.cleaner)
            try:
                client, addr = serv_sock.accept()
            except socket.timeout:
                continue

            try:
                time.sleep(0.001)
                data = json.loads(client.recv(1024))
                self.tasks_query.send((client, data))
            except (json.decoder.JSONDecodeError, ConnectionResetError):
                print('Someone closed connection')


if __name__ == '__main__':
    main(HOST, PORT)
