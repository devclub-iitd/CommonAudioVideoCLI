import ffmpeg
import sys
import os
import subprocess
import re


BITRATE = 1000*16

def path2title(path):
    return path.split('/')[-1:][0]

def get_multiplier(quality):
    """ A multiplier to decide bitrate from the quality string """

    if quality == 'low':
        return 5
    elif(quality == 'medium'):
        return 6
    elif (quality == 'good'):
        return 7
    elif(quality == 'high'):
        return 8
    return 6


def extract(path, quality="medium"):
    """ Extractor function utilizing ffmpeg to extract audio from a given video file """

    try:
        file = ffmpeg.input(path)
        output_path = path[:-3]+"ogg"
        if(os.path.exists(output_path)):
            print(f"[#] Audio file {path2title(output_path)} already exists")
            return output_path
        print("[+] Extracting audio for file %s" % (path2title(path)))
        file.audio.output(output_path, acodec='libvorbis',
                          audio_bitrate=BITRATE*get_multiplier(quality), loglevel=0).run()
        print("[+] Extraction completed for file %s" % (path2title(output_path)))

    except Exception as ex:
        print(f"[-] There was an error extracting the audio for path {path2title(path)}: ", ex)
        sys.exit(-1)

    return output_path

def get_duration(file):
    cmd = "ffmpeg -i %s" % file
    time_str = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()
    time_str = re.search('Duration: (.*), start',time_str[0].decode()).groups()[0]
    hours, minutes, seconds = time_str.split(':')
    return int(hours)*3600 + int(minutes)*60 + float(seconds)

def convert2mkv(path):
    out_path = path+'.mkv'
    if(os.path.exists(out_path)):
        return out_path
    try:
        ffmpeg.input(path).output(out_path,codec='copy',loglevel=0).run()
        print(f"[+] Successfully converted {path2title(path)} to MKV format")
        return out_path
    except Exception as e:
        print(f"[-] An error occured while converting {path2title(path)} to MKV: ",e)
        raise e