import argparse
import sys
import signal
import time
import os
import subprocess
from multiprocessing import Process, Pool
from multiprocessing.managers import BaseManager
from itertools import product

from server_comm import ServerConnection
from vlc_comm import player
from util import get_videos
from audio_extract import extract


def parse():
    parser = argparse.ArgumentParser(description="Route audio of a video file through a local server.")
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('-f', '--file', required=True, dest="f",
                        help="Path to video files or directory containing video files", type=str, action="append")
    parser.add_argument('-s', '--sub', dest="sub",
                        help="Load subtitle File", type=str, action="store")
    parser.add_argument(
        '--qr', help="Show qr code with the link", dest="qr", action="store_true")
    parser.add_argument(
        '--control', help="only host can control play/pause signals", dest="onlyHost", action="store_true")
    parser.add_argument('--force-rebuild',help='Force rebuild of the local server',dest='rebuild',action='store_true')
    parser.add_argument('--audio-quality', dest="q", help="Audio quality to sync from",
                        choices=["low", "medium", "good", "high"], type=str, default="medium")

    group.add_argument('--web', help="Force routing through a web server",
                       dest="web", action="store_true")
    args = parser.parse_args()
    videos = []
    for i in range(len(args.f)):
        args.f[i] = os.path.abspath(args.f[i])
        videos.extend(get_videos(args.f[i]))
    args.f = videos
    return args


def convert_async(paths):
    """ Converts video files to audio files asynchronously
    using a pool of processes """
    pool = Pool()
    files = []
    st = time.perf_counter()
    print("Converting files")
    p = pool.starmap_async(extract, product(
        paths, [args.q]), callback=files.extend)

    p.wait()
    print(f"Completed extraction of {len(paths)} file(s) in {time.perf_counter()-st} seconds")
    return files


def exitHandler(*args, **kwargs):
    # print("\nExiting now..Goodbye!")
    if(os.path.exists('cache')):
        try:
            os.remove('cache')
        except Exception as e:
            # if(e or not e):
                # print("Cleared Cache")
            pass
    os.system("killall node 2> /dev/null")
    sys.exit(0)


SERVER_PATH = '../../CommonAudioVideoServer/'


def spawn_server():
    if(not os.path.exists(SERVER_PATH)):
        print("Invalid Server Path, Try reinstalling the package")
        sys.exit(-1)

    if(not os.path.exists(SERVER_PATH+'node_modules')):
        print("Configuring the server ..")
        subprocess.Popen('npm install'.split(), stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, cwd=os.getcwd()+'/'+SERVER_PATH).wait()
        print("Server configuration complete ..")
    
    if(args.rebuild):
        print("Building server ..")
        subprocess.Popen('npm run compile'.split(), stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, cwd=os.getcwd()+'/'+SERVER_PATH).wait()
        print("Server build successfull ..")

    print("Initializing Server ..")
    proc = subprocess.Popen(
        'npm start'.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd()+'/'+SERVER_PATH)
    for line in iter(proc.stdout.readline, ""):
        if(b'npm ERR!' in line):
            print(line)
            print("An error has occured while starting the server\nRestarting the server")
            sys.exit(-1)
        if(b'Press CTRL-C to stop' in line):
            break

def initialize(videos,server,first=False):
    audio = convert_async(videos)

    for video in videos:
        player.enqueue(video)

        title = video.split('/')[-2:-1][0].split('.')[0]
        if args.web:
            server.upload(title, video[:-3]+"ogg")
        else:
            server.addAudioPath(video[:-3]+"ogg")

        if(first):
            server.create_room(title=title)
            player.play()
            player.pause()
            player.seek(0)
            
        else:
            server.add_track(title=title)


if __name__ == '__main__':

    signal.signal(signal.SIGINT, exitHandler)

    args = parse()
    if(not args.web):
        spawn_server()


    player.launch(args.sub)

    BaseManager.register('ServerConnection', ServerConnection)
    manager = BaseManager()
    manager.start()
    server = manager.ServerConnection()
    server.start_listening()

    Process(target=player.update, args=(server, )).start()


    initialize([args.f[0]],server=server,first=True)

    if(len(args.f)>1):
        Process(target=initialize,kwargs={"videos":args.f[1:],"server":server,"first":False}).run()


    while True:
        print(player.getState())
        time.sleep(1)
