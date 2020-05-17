import socketio
# import time
SERVER_ADDR = "http://localhost:5000"


# this is used internally by ServerConnection
class VLC_signals(socketio.ClientNamespace):
    def bind(self):
        """ Binds the player instance to this class instance. """

        from vlc_comm import player
        self.player = player

    """ Functions with name like on_event are executed when a signal named 'event' is recieved from the server. """

    def on_connect(self):
        print('connected')

    def on_disconnect(self):
        print('disconnected')

    def on_play(self, *args, **kwargs):
        self.player.play()

    def on_pause(self, *args, **kwargs):
        self.player.pause()

    def on_seek(self, position, *args, **kwargs):
        print("Seek signal for ", position)
        self.player.seek(position)


class ServerConnection():   # Class that handles all connections to the server.
    def __init__(self):
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:3000')

    def send(self, signal, data):
        """ Used to send data to the server with a corresponding signal"""

        self.sio.emit(signal, data)

    def start_listening(self):
        """ Establish connection to the server and start listening for signals from the server """

        self.signals = VLC_signals('/')
        self.signals.bind()
        self.sio.register_namespace(self.signals)

    def upload(self, fileName, path):
        """ Uploads audio file to the webserver """
        print("Uploading to server")
        import requests
        url = f"{SERVER_ADDR}/upload/"
        files = {'file': (fileName, open(path, 'rb'), 'audio/ogg')}
        r = requests.post(url=url, files=files)
        print(r.json())
