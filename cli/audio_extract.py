import ffmpeg
import sys

BITRATE = 1000*16


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
        print("Extracting audio for file %s" % (path))
        file.audio.output(output_path, acodec='libvorbis',
                          audio_bitrate=BITRATE*get_multiplier(quality), loglevel=0).run()
        print("Extraction completed for file %s" % (output_path))

    except:
        print("There was an error converting the file")
        sys.exit(-1)

    return output_path
