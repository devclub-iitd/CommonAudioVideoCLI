import socketio
import time
from util import Singleton
import vlc_comm


class VLC_signals(socketio.ClientNamespace): # this is used internally by ServerConnection
    def bind(self):
        self.player = vlc_comm.VLCplayer()
    def on_connect(self):
        print('connected')

    def on_disconnect(self):
        print('disconnected')

    def on_play(self,*args, **kwargs):
        self.player.play()
    
    def on_pause(self,*args, **kwargs):
        self.player.pause()

    def on_seek(self,position,*args, **kwargs):
        print("Seek signal for ",position)
        self.player.seek(position)

class ServerConnection(metaclass=Singleton):
    def __init__(self):
        super().__init__()
        sio = socketio.Client()
        self.signals = VLC_signals('/')
        self.signals.bind()
        sio.register_namespace(self.signals)
        sio.connect('http://localhost:3000')

    def send(self,signal,data):
        data['last_updated'] = time.time()
        self.signals.emit(signal,data)

server = ServerConnection()
