import socketio
from vlc_comm import VLC_instance

class VLC_signals(socketio.ClientNamespace):
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
        
def communicate(vlc_instance):  
    sio = socketio.Client()
    vlc_signals = VLC_signals('/')
    vlc_signals.bind(vlc_instance)
    sio.register_namespace(vlc_signals)
    sio.connect('http://localhost:3000')

    return vlc_signals




