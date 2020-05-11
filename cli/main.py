import argparse
import audio_extract
from vlc_comm import VLC_instance
import time

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

instance = VLC_instance(1234)
for file_path in args.f:
    instance.enqueue(file_path)
    instance.play()
    instance.pause()
    
    # instance.pause()
    # time.sleep(2)
    # instance.play()
    time.sleep(2)
    # instance.faster_playback()
    instance.getState()



    