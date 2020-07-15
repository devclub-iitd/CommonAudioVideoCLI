import socketio
import time
import psutil

from util import path2title

SERVER_ADDR = "localhost"


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
        self.player.seek(
            int(time.time() - state['last_updated'] + state['position']))

    def on_createRoom(self, *args,  **kwargs):
        self.roomId = args[0]['roomId']
        from main import parse
        args = parse()
        url = "http://%s:5000/client/stream/?roomId=%s"
        if(args.web):
            url = url % (SERVER_ADDR, self.roomId)
        else:
            addrs = psutil.net_if_addrs()
            local_addr = addrs['wlp3s0'][0].address       # modify
            url = url % (local_addr, self.roomId)
        from util import print_url
        print_url(url)
        if(args.qr):
            from util import print_qr
            print("Or scan the QR code given below")
            print_qr(url)


class ServerConnection():
    # Class that handles all connections to the server
    def __init__(self):
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:5000')
        self.tracks = {}

        # For testing purposes...
        # self.trackId = '5ed554389cd979784f6926e3'   # Bella-Caio
        # self.trackId = '5ed88aae25f4787bea4cc07f'     # Dark
        # self.trackId = '5ee350d3c67ae85cae6f669c'    # mha op

    def send(self,  signal,  data):
        """ Used to send data to the server with a corresponding signal"""
        self.sio.emit(signal,  data)

    def start_listening(self):
        """ Establish connection to the server and start listening for signals from the server """

        self.signals = VLC_signals('/')
        self.signals.bind()
        self.sio.register_namespace(self.signals)

    def track_change(self,videoPath):
        print("Changing track to ", videoPath)
        self.send('changeTrack',{
            self.tracks[videoPath][0] : self.tracks[videoPath][1]
        })

    def add_track(self, videoPath):
        self.send('addTrack',{
            "title": path2title(videoPath),
            self.tracks[videoPath][0] : self.tracks[videoPath][1]
        })

    def create_room(self, videoPath):
        self.send('createRoom',{
            "title": path2title(videoPath),
            self.tracks[videoPath][0] : self.tracks[videoPath][1]
        })

    def upload(self, videoPath ,audioPath):
        """ Uploads audio file to the webserver """
        print("Uploading to server")
        import requests
        url = f"http://{SERVER_ADDR}:5000/api/upload/"
        files = {'file': (path2title(videoPath),  open(audioPath,  'rb'),  'audio/ogg')}
        r = requests.post(url=url, files=files, data={"title": path2title(videoPath)})

        self.tracks[videoPath]= ("trackId" ,r.json()['trackId'])

    def addAudioPath(self, videoPath, audioPath):
        self.tracks[videoPath] = ("audioPath", audioPath)
