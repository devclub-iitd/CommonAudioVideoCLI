import argparse
from audio_extract import extract
import time
from multiprocessing import Process, Pool
from itertools import product
import threading

from vlc_comm import player
from server_comm import server


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

parser.add_argument('-f', '--file', required=True, dest="f",
                    help="Path to video file", type=str, action="append")
parser.add_argument('-s', '--sub', dest="sub",
                    help="Load subtitle File", type=str, action="store")
parser.add_argument(
    '--qr', help="Show qr code with the link", dest="qr", action="store_true")
parser.add_argument('--audio-quality', dest="q", help="Audio quality to sync from",
                    choices=["low", "medium", "good", "high"], type=str, default="medium")

group.add_argument('--local', help="Host locally",
                   dest="local", action="store_true")
group.add_argument('--web', help="Route through a web server",
                   dest="web", action="store_true")

args = parser.parse_args()


def send_to_server(name):   # TO be implemented in server_comm.py
    print(f"Files ..{name}.. sending to server")


def convert_async():
    pool = Pool()
    st = time.perf_counter()
    print("Converting files")
    p = pool.starmap_async(extract, product(
        args.f, [args.q]), callback=send_to_server)

    p.wait()
    print(
        f"Completed execution of {len(args.f)} processes in {time.perf_counter()-st} seconds")


######################################


time.sleep(1)
player.launch()
Process(target=player.update,daemon=True).start()
# threading.Thread(target=player.update).start()

server.send('play',{})
server.send('seek',{"position":200})

for file_path in args.f:
    print(args.f)
    player.enqueue(file_path)
    time.sleep(2)
    player.play()
    # for line in iter(player.proc.stdout.readline,""):
    #     print(line)
    while(True):
        print(player.getState())
        time.sleep(1)
