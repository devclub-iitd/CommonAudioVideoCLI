import socketio
import time
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

    def on_userId(self,  data):
        print('userId is ',  data)

    def on_disconnect(self):
        print('disconnected')

    def on_play(self,  *args,  **kwargs):
        state = args[0]
        print("Play signal recieved with the following data",  state)
        self.player.play()

    def on_pause(self,  *args,  **kwargs):
        state = args[0]
        print("Pause signal recieved with the following data", state)
        self.player.pause()

    def on_seek(self,  *args,  **kwargs):
        state = args[0]
        print("Seek signal recieved with the following data", state)
        self.player.seek(int(time.time() - state['last_updated'] + state['position']))

    def on_createRoom(self, *args,  **kwargs):
        self.roomId = args[0]['roomId']
        url = f"http://localhost:5000/client/stream/?roomId={self.roomId}"
        print(f"Please visit {url}")
        from main import parse
        if(parse().qr):
            from util import print_qr
            print("Or scan the QR code given below")
            print_qr(url)


class ServerConnection():
    # Class that handles all connections to the server
    def __init__(self):
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:5000')

        # For testing purposes...
        self.trackId = '5ed554389cd979784f6926e3'   # Bella-Caio
        # self.trackId = '5ed88aae25f4787bea4cc07f'     # Dark

    def send(self,  signal,  data):
        """ Used to send data to the server with a corresponding signal"""
        self.sio.emit(signal,  data)

    def start_listening(self):
        """ Establish connection to the server and start listening for signals from the server """

        self.signals = VLC_signals('/')
        self.signals.bind()
        self.sio.register_namespace(self.signals)

    def create_room(self, title, onlyHost):
        self.send('createRoom', {'title': title, 'trackId': self.trackId, 'onlyHost': onlyHost})

    def upload(self,  fileName,  path):
        """ Uploads audio file to the webserver """
        print("Uploading to server")
        import requests
        url = f"{SERVER_ADDR}/api/upload/"
        files = {'file': (fileName,  open(path,  'rb'),  'audio/ogg')}
        r = requests.post(url=url, files=files, data={"title": fileName})
        print(r.json())
        self.trackId = r.json()['trackId']
