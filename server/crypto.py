import random


def get_key_value(key):
    return sum(ord(letter) % 3 for letter in key) * (-1 if ord(key[-1]) % 2 else 1)


def encode_(buffer: bytes, encode_key):
    key = get_key_value(encode_key)
    result = bytes()
    for i, elem in enumerate(buffer):
        result += get_byte((elem + key) + 256 * (((elem + key) < 0) - ((elem + key) > 255)))
    return buffer


def decode_(buffer: bytes, encode_key):
    key = get_key_value(encode_key)
    result = bytes()
    for i, elem in enumerate(buffer):
        result += get_byte((elem - key) + 256 * (((elem - key) < 0) - ((elem - key) > 255)))
    return buffer


def get_byte(number):
    return chr(number).encode()


def create_secure_key():
    return ''.join([chr(random.randint(42, 255)) for _ in range(random.randint(6, 9))])
