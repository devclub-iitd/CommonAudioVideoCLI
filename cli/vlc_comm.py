import socket
import sys
import subprocess
import time
import re
import json

from util import *

class VLC_instance:
    def __init__(self,port):
        self.port = port

    def update(self):
        messages = ["get_time\n", "get_title\n", "status\n"]
        state={}
        while True:
            for message in messages:
                key = message.strip()
                state[key]=get_cmd_resp(self.sock,message)
                if("status" == key):
                    try:
                        state[key] = re.search("state (.*) ", state[key]).groups()[0]
                    except:
                        state[key] = ""
            open('cache','w').write(json.dumps(state))

    @wait_until_error
    def getState(self):
        return json.loads(open('cache','r').read())

    def launch(self):
        bashCommand = 'vlc --extraintf rc --rc-host localhost:%d' % (self.port)
        print(bashCommand)
        subprocess.Popen(bashCommand.split())

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', self.port)
        wait_until_error(self.sock.connect,timeout=2)(self.server_address)
        time.sleep(1)
        self.sock.recv(1024)

    def play(self):
        message = 'play\n'.encode()
        send_until_writable()(self.sock.sendall,self.sock,message)
            
    def pause(self):
        message='pause\n'.encode()
        send_until_writable()(self.sock.sendall, self.sock, message)

    def seek(self,position):
        message=f"seek {position}\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
    
    def enqueue(self,filePath):
        message=f"enqueue {filePath}\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        
    def faster_playback(self):
        message='faster\n'.encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
    
    def slower_playback(self):
        message='slower\n'.encode()
        send_until_writable()(self.sock.sendall, self.sock, message)


