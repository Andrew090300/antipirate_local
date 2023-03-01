import os
import subprocess
from pathlib import Path


def convert_to_mp3(source):
    sound_format = Path(str(source)).suffix
    file_before_conversion = source
    converted_file = str(
        source)[:-3] + '.mp3' if len(sound_format) == 3 else str(
        source)[:-4] + '.mp3'
    subprocess.call(['ffmpeg', '-i', f'{source}', f'{converted_file}'])
    os.remove(file_before_conversion)
    return converted_file
