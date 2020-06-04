# Common Audio Video CLI


## Getting Started

### Prerequisites

To run this project you need to have python 3.6 or higher installed

### Installing

**Cloning the Repository**

```
$ git clone https://github.com/devclub-iitd/CommonAudioVideoCLI.git

$ cd CommonAudioVideoCLI
```

**Installing dependencies**

```
$ pip3 install -r requirements.txt
```

**Running the CLI**

```
$ python3 cli/main.py [--flags]
```

## CLI flags
| FLAG NAME | arguments | usage | required | default
|--|--|--|--|--
| - - file / -f | path to one or more video files | indicates which videos are to be converted and queued | yes
| -- sub / -s |  path to one more subtitle files in order | adds the subtitle track to the playback | no| -
| -- qr| - |encodes the invite link as a qr code and prints it to the console| no| false
| --audio-quality| low/medium/good/high | the quality of the audio to be extracted from the video file| no | medium
| --local |	- | set up local web server on the host for streaming
|--web| - | use already hosted webserver 	
|--control| - | only the host can control playback



## Socket events

| EVENT NAME | action 
|--|--
|connect | emitted at the beginning to establish connection
|disconnect| emitted when session ends
| play | has 2 functions -- starts the playback <br> of enqueued song, if no video is loaded,<br> otherwise resumes the playback from where <br> it was paused	
| pause | pauses the playback 
| seek  | seeks to the given time in the playback

Socket events, both sent and received follow the same structure as shown above and additionally, each event has the following information along with the event type :--
- epoch time -- the time in milliseconds when the command is being issued 
- position -- the position of the video/audio playback


**Note:** The server has to create a room when 'connect' message is sent from the CLI, and return in response, the room URL. Any further messages from this socket should be considered as being emitted by the host of that room.

## Built With
- Python
- [ArgParser](https://pypi.org/project/argparse/) - create the command line interface 
- [ffmpeg](https://pypi.org/project/ffmpeg-python/) - extract audio from vidoe file
- [subprocess](https://docs.python.org/3/library/subprocess.html) - issue bash commands from python and read VLC logs to catch play/pause events.
- [socket-io Client](https://python-socketio.readthedocs.io/en/latest/) - websocket to connect and send signals to server
- [socket](https://docs.python.org/3/library/socket.html) - tcp sockets to issue commands to VLC player

## License

[MIT](LICENSE)

