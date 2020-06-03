import argparse
from audio_extract import extract
import time
from multiprocessing import Process, Pool
from multiprocessing.managers import BaseManager
from itertools import product

from server_comm import ServerConnection
from vlc_comm import player
from util import getRandomString

def parse():
    parser = argparse.ArgumentParser()
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

    group.add_argument('--local', help="Host locally",
                       dest="local", action="store_true")
    group.add_argument('--web', help="Route through a web server",
                       dest="web", action="store_true")
    
    return parser.parse_args()


def send_to_server(name):   # TO be implemented in server_comm.py
    print(f"File ..{name}.. sending to server")
    time.sleep(5)
    print("File sent to server")


def convert_async():    # Converts video files to audio files asynchronously using a pool of processes
    pool = Pool()
    files = []
    st = time.perf_counter()
    print("Converting files")
    p = pool.starmap_async(extract, product(
        args.f, [args.q]), callback=files.extend)

    p.wait()
    print(
        f"Completed extraction of {len(args.f)} files in {time.perf_counter()-st} seconds")
    return files

######################################


if __name__ == "__main__":
    args = parse()
    # audio_files = convert_async()
    print(args.onlyHost)
    player.launch()

    BaseManager.register('ServerConnection', ServerConnection)
    manager = BaseManager()
    manager.start()
    server = manager.ServerConnection()
    server.start_listening()
    
    Process(target=player.update, args=(server,)).start()

    for i in range(len(args.f)):
        player.enqueue(args.f[i])
        player.pause()
        try:
            title = player.getState()['title']
        except:
            title=getRandomString(10)
        
        # server.upload(getRandomString(5),audio_files[i])
        server.create_room(title,args.onlyHost)
        
        

    # To do --> Add support for changing items in playlist.
    for i in range(len(args.f)):
        player.seek(0)
        # player.play()

        while(True):
            print(player.getState())
            time.sleep(1)
