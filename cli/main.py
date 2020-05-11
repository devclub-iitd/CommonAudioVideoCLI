import argparse
import audio_extract
from vlc_comm import VLC_instance
import time
import threading
import vlc_comm


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

parser.add_argument('-f','--file',required=True,dest="f",help="Path to video file",type=str,action="append")
parser.add_argument('-s','--sub',dest="sub",help="Load subtitle File",type=str,action="store")
parser.add_argument('--qr',help="Show qr code with the link",dest="qr",action="store_true")
parser.add_argument('--audio-quality',dest="q",help="Audio quality to sync from",choices=["low","medium","good","high"],type=str,default="medium")

group.add_argument('--local',help="Host locally",dest="local",action="store_true")
group.add_argument('--web',help="Route through a web server",dest="web",action="store_true")

args=parser.parse_args()
# audio_file_paths = audio_extract.extract(args.f,args.q)

#init server conf.... create room

player = VLC_instance(1234)
player.launch()

b = threading.Thread(target=player.update, name='update')
b.start()

for file_path in args.f:
    player.enqueue(file_path)
    player.play()
    time.sleep(4)
    print(player.state)
    player.seek(60)
    time.sleep(3)
    print(player.state)
    time.sleep(5)
    print(player.state)
    time.sleep(5)
    print(player.state)
    # print(player.state)
    # time.sleep(5)
    # print(player.state)
    # player.seek(60)
    # time.sleep(2)
    # print(player.state)


    
