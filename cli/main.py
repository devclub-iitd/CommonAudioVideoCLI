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
from util import getRandomString
from audio_extract import extract


def parse():
    parser = argparse.ArgumentParser(description="Route audio of a video file through a local server.")
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('-f', '--file', required=True, dest="f",
                        help="Path to video file", type=str, action="append")
    parser.add_argument('-s', '--sub', dest="sub",
                        help="Load subtitle File", type=str, action="store")
    parser.add_argument(
        '--qr', help="Show qr code with the link", dest="qr", action="store_true")
    parser.add_argument(
        '--control', help="only host can control play/pause signals", dest="onlyHost", action="store_true")
    parser.add_argument('--audio-quality', dest="q", help="Audio quality to sync from",
                        choices=["low", "medium", "good", "high"], type=str, default="medium")

    group.add_argument('--web', help="Force routing through a web server",
                       dest="web", action="store_true")
    args = parser.parse_args()
    for i in range(len(args.f)):
        args.f[i] = os.path.abspath(args.f[i])

    return args


def convert_async():
    """ Converts video files to audio files asynchronously
    using a pool of processes """
    pool = Pool()
    files = []
    st = time.perf_counter()
    print("Converting files")
    p = pool.starmap_async(extract, product(
        args.f, [args.q]), callback=files.extend)

    p.wait()
    print(f"Completed extraction of {len(args.f)} file(s) in {time.perf_counter()-st} seconds")
    return files


def exitHandler(*args, **kwargs):
    print("\nExiting now..Goodbye!")
    if(os.path.exists('cache')):
        try:
            os.remove('cache')
        except Exception as e:
            if(e or not e):
                print("Cleared Cache")
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
    print("Building server ..")
    subprocess.Popen('npm run compile'.split(), stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, cwd=os.getcwd()+'/'+SERVER_PATH).wait()
    print("Server build successfull ..")
    print("Initializing Server ..")
    proc = subprocess.Popen(
        'npm start'.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd()+'/'+SERVER_PATH)
    for line in iter(proc.stdout.readline, ""):
        if(b'npm ERR!' in line):
            print("An error has occured while starting the server")
            sys.exit(-1)
        if(b'Press CTRL-C to stop' in line):
            break


if __name__ == '__main__':

    signal.signal(signal.SIGINT, exitHandler)

    args = parse()
    if(not args.web):
        spawn_server()

    audio_files = convert_async()

    player.launch()

    BaseManager.register('ServerConnection', ServerConnection)
    manager = BaseManager()
    manager.start()
    server = manager.ServerConnection()
    server.start_listening()

    Process(target=player.update, args=(server, )).start()

    for i in range(len(args.f)):
        player.enqueue(args.f[i])
        player.pause()
        try:
            title = player.getState()['title']
        except Exception as e:
            if(e or not e):
                title = getRandomString(10)

        if args.web:
            # server.upload(title, audio_files[i])
            pass
        else:
            server.addAudioPath(audio_files[i])

        server.create_room(title)

    # To do --> Add support for changing items in playlist.

    for i in range(len(args.f)):
        player.seek(0)
        # player.play()
        while True:
            # print(player.getState())
            time.sleep(1)
