import socket
import sys
import subprocess
import time
class VLC_instance:

    def __init__(self,port):
        self.port = port
        self.state = {}


    # def getState(self):
    #     state = dict()
    #     messages = ["is_playing\n"]  # is_playing working??  add other states like get_time.....
    #     for message in messages:
    #         print(f"for message {message}")
    #         state[message] = self.sock.sendall(message.encode('utf-8'))
    #         total_data=''
    #         data = self.sock.recv(1024)
    #         print(data.decode())
    #         data = self.sock.recv(1024)
    #         print(data.decode())

    #         state[message] = data.decode()

    #     return state

    def update(self):
        messages = ["is_playing\n","get_time\n","get_title\n"]
        while True:
            for message in messages:
                key = message.strip()
                self.sock.sendall(message.encode())
                time.sleep(0.5)
                self.state[key] = self.sock.recv(1024).decode().replace('>', '').strip()
   

    def launch(self):
        bashCommand = 'vlc --extraintf rc --rc-host localhost:%d' % (self.port)
        print(bashCommand)
        subprocess.Popen(bashCommand.split())
        time.sleep(2)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', self.port)
        # self.sock.setblocking(True)
        self.sock.connect_ex(self.server_address)
        time.sleep(1)
        self.sock.recv(1024)
    
    def play(self):
        self.sock.sendall('play\n'.encode('utf-8'))
    
    def pause(self):
        self.sock.sendall('pause\n'.encode('utf-8'))

    def seek(self,position):
        self.sock.sendall(f"seek {position}\n".encode('utf-8'))
    
    def enqueue(self,filePath):
        self.sock.sendall(f"enqueue {filePath}\n".encode('utf-8'))
        

    def faster_playback(self):
        self.sock.sendall('faster\n'.encode('utf-8'))
    
    def slower_playback(self):
        self.sock.sendall('slower\n'.encode('utf-8'))

