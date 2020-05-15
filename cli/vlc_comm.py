import socket
# import sys
import subprocess
import time
import re
import json
from util import send_until_writable, wait_until_error

PORT = 1234


class VLCplayer():  # Class that manages the VLC player instance on the machine.

    def __init__(self, port=PORT, sub=None):
        self.sub = sub
        self.port = port
        self.proc = None

    @wait_until_error
    def readState(self):
        """ This reads the JSON state from cache of the video that is currently playing """

        return json.loads(open('cache', 'r').read())

    def launch(self):
        """ Launches a VLC instance """

        bashCommand = 'vlc --extraintf rc --rc-host localhost:%d -vv' % (
            self.port)
        if(self.sub is not None):
            bashCommand += " --sub-file %s" % (self.sub)

        # Start a subprocess to execute the VLC command
        self.proc = subprocess.Popen(bashCommand.split(
        ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        # Create a socket connection to the RC interface of VLC that is listening for commands at localhost:1234
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', self.port)
        wait_until_error(self.sock.connect, timeout=5)(self.server_address)

        # Dump any trash data like welcome message that we may recieve from the server after connecting
        self.sock.recv(1024)

    """ The following functions send a specific command to the VLC instance using the socket connection """

    def play(self):
        message = 'play\n'.encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def pause(self):
        message = 'pause\n'.encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def seek(self, position):
        message = f"seek {position}\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def enqueue(self, filePath):
        message = f"enqueue {filePath}\n".encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def faster_playback(self):
        message = 'faster\n'.encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def slower_playback(self):
        message = 'slower\n'.encode()
        send_until_writable()(self.sock.sendall, self.sock, message)
        time.sleep(0.5)

    def update(self):
        """ Keeps the VLC instance state updated by parsing the VLC logs that are generated """
        parse_logs(self)

    def getState(self):
        """ Interprets the meaning of the dumped data in cache
        by calculating the live position of the video from the last_updated and postition keys
        in the data. It returns the live state of the video """

        player = self
        state = player.readState()
        if state is None:
            return
        if('last_updated' in state.keys()):
            initial_pos = state['position']
            extra = time.time() - \
                float(state['last_updated']) if state['is_playing'] else 0
            final_pos = initial_pos + extra
            state['position'] = final_pos
            state.pop('last_updated')
            return state


def parse_logs(player):
    """ A function that is to be run in a seperate process to parse VLC logs
    and get user events like START,STOP,PLAY,PAUSE,SEEK and accordingly respond
    by sending the data to the server. """

    import server_comm
    # Another instance to send the data since somehow sockets were inaccessible by this process
    other_connection = server_comm.ServerConnection()

    state = player.readState()
    if(state is None):
        state = {}

    def on_title(match):
        state['title'] = match.groups()[0]

    def on_duration(match):
        if 'duration' not in state.keys():
            state['duration'] = match.groups()[0]

    def on_start(match):
        state['position'] = 0.0
        state['is_playing'] = True
        state['last_updated'] = time.time()

    def on_stop(match):
        state['is_playing'] = False
        del state['duration']
        del state['title']
        state['position'] = 0.0
        state['last_updated'] = time.time()

    def on_play(match):
        if not state['is_playing']:
            state['is_playing'] = True
            state['last_updated'] = time.time()
            other_connection.send('play', state)

    def on_pause(match):
        if state['is_playing']:
            state['is_playing'] = False
            state['position'] = player.getState()['position'] if player.getState() is not None else 0
            state['last_updated'] = time.time()
            other_connection.send('pause', state)

    def on_seek(match):
        match = match.groups()[0]
        if ('i_pos' in match):
            # Match is the absolute duratoin
            match = match.split('=')[1].strip()
            state['position'] = float(match)/1000000.0
            state['last_updated'] = time.time()

        # This is used when seek occurs through the slider
        else:
            # Match is the percentage of the total duration
            match = match[:-1]
            state['position'] = float(
                match)*float(state['duration'])/100000.0
            state['last_updated'] = time.time()
        other_connection.send('seek', state)

    REGEX_DICT = {
        "Title=(.*)$" : on_title,
        "Duration=(.*)$" : on_duration,
        "seek request to (.*)%*$" : on_seek,
        "toggling resume$" : on_pause,
        "toggling pause$": on_play,
        "pts: 0" : on_start,
        "dead input" : on_stop,
    }

    def get_regex_match(line):
        for regex in REGEX_DICT:
            match = re.search(regex,line)
            if match:
                return regex,match
        return None,None

    # Continuosly read the VLC logs
    for line in iter(player.proc.stdout.readline, ""):

        regex,match = get_regex_match(line)
        if match:
            REGEX_DICT[regex](match)

        # Dump the parsed data into cache
        open('cache', 'w').write(json.dumps(state))


player = VLCplayer()
