import time
import socket
from select import select
import pyqrcode


class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance



def wait_until_error(f, timeout=0.5):
    def inner(*args, **kwargs):
        st = time.perf_counter()
        while(time.perf_counter() - st < timeout):
            try:
                return f(*args, **kwargs)
            except:
                continue
    return inner


def get_cmd_resp(socket, cmd, timeout=0.5):
    st = time.perf_counter()
    socket.sendall(cmd.encode())
    recvd, resp = b"", ""
    while(b'>' not in recvd and time.perf_counter() - st < timeout):
        recvd += socket.recv(1024)
        resp = recvd.decode().replace('>', '').strip()
        if(resp == ""):
            recvd.replace(b'>', b'')
    return resp


def send_until_writable(timeout=0.5):
    def inner(f, socket, message):
        st = time.perf_counter()
        while(time.perf_counter() - st < timeout):
            if(check_writable(socket)):
                return f(message)
    return inner


def check_writable(socket):
    a, writable, b = select([], [socket], [], 60)
    return writable == [socket]

def print_qr(url):
    image = pyqrcode.create(url)
    image.svg('invite_link.svg', scale=1)
    print(image.terminal(quiet_zone=1))



