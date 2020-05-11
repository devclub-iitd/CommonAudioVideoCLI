import socket
import sys
import subprocess
import time

class VLC_instance:
    def __init__(self,port):
        bashCommand = 'vlc --extraintf cli --rc-host localhost:1234'
        subprocess.Popen(bashCommand.split())
        time.sleep(2)

        print('here')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', port)
        print(f"starting up on {self.server_address}")
        self.sock.connect(self.server_address)
        print('done')
        data = self.sock.recv(1024)
        print(data)

    def getState(self):
        state = dict()
        messages = ["is_playing\n"]  # is_playing working??  add other states like get_time.....
        for message in messages:
            print(f"for message {message}")
            state[message] = self.sock.sendall(message.encode('utf-8'))
            total_data=''
            data = self.sock.recv(1024)
            print(data.decode())
            data = self.sock.recv(1024)
            print(data.decode())

            state[message] = data.decode()

        return state
    
    def play(self):
        self.sock.sendall('play\n'.encode('utf-8'))
        time.sleep(5)
    
    def pause(self):
        self.sock.sendall('pause\n'.encode('utf-8'))

    def seek(self,position):
        message = f"seek {position}\n"
        self.sock.sendall(message.encode('utf-8'))
    
    def enqueue(self,filePath):
        message = f"enqueue {filePath}\n"
        self.sock.sendall(message.encode('utf-8'))
        

    def faster_playback(self):
        self.sock.sendall('faster\n'.encode('utf-8'))
    
    def slower_playback(self):
        self.sock.sendall('slower\n'.encode('utf-8'))

        


        


