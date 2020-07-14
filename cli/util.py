import time
import os
from select import select
import pyqrcode
import random


def wait_until_error(f, timeout=0.5):
    """ Wait for timeout seconds until the function stops throwing any errors. """

    def inner(*args, **kwargs):
        st = time.perf_counter()
        while(time.perf_counter() - st < timeout or timeout < 0):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if(e or not e):
                    continue
    return inner


def send_until_writable(timeout=0.5):
    """ This will send a message to the socket only when it is writable and wait for timeout seconds
    for the socket to become writable, if the socket was busy. """

    def inner(f, socket, message):
        st = time.perf_counter()
        while(time.perf_counter() - st < timeout):
            if(check_writable(socket)):
                return f(message)
    return inner


def check_writable(socket):
    """ Checks whether the socket is writable """

    a, writable, b = select([], [socket], [], 60)
    return writable == [socket]


def print_qr(url):
    """ Prints a QR code using the URL that we recieved from the server. """

    image = pyqrcode.create(url)
    image.svg('invite_link.svg', scale=1)
    print(image.terminal(quiet_zone=1))


def getRandomString(length):

    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    out = ""
    for i in range(length):
        out += charset[random.randint(0, len(charset)-1)]
    return out

def get_videos(path):
    if(os.path.isfile(path)):
        if (path[-3:] in ['mkv','mp4']):
            return [path]
        return []
    if(os.path.isdir(path)):
        ans = []
        for file in os.listdir(path):
            ans.extend(get_videos(path+'/'+file))
        return ans
