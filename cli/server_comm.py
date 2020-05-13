import socketio
from vlc_comm import VLC_instance
import time

class VLC_signals(socketio.ClientNamespace): # this is used internally by ServerConnection
    def bind(self,player):
        self.player = player

    def on_connect(self):
        print('connected')

    def on_disconnect(self):
        print('disconnected')

    def on_play(self):
        self.player.play()
    
    def on_pause(self):
        self.player.pause()

    def on_seek(self,position):
        self.player.seek(position)

class ServerConnection:
    def __init__(self,player):
        sio = socketio.Client()
        self.signals = VLC_signals('/')
        self.signals.bind(player)
        sio.register_namespace(self.signals)
        sio.connect('http://localhost:3000')

    def send_play(self):
        self.signals.emit('play')
    
    def send_pause(self):
        self.signals.emit('pause')

    def send_seek(self,position):
        data={
            'position':position,
            'timestamp': time.time()*1000
        }
        self.signals.emit('seek',data)

    





