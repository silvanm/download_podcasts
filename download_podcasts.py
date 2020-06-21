#!/usr/local/bin/python3
import argparse
import cgi
import os
import shutil
import arrow
import tempfile
from urllib.parse import urlparse
from urllib.request import urlretrieve, urlopen
from podcastparser import parse
from gtts import gTTS
from settings import PODCASTS

TMPPATH = tempfile.gettempdir()

DIRECTORY = arrow.utcnow().format('YYYY-MM-DD')

parser = argparse.ArgumentParser(description='Download, normalize MP3\'s and assign a spoken tag.')
parser.add_argument('destpath', help='Where to store the downloaded files')
parser.add_argument('-b', '--boost', action='store_true',
                    help='Run the file through the compressor')

args = parser.parse_args()

DESTPATH = os.path.join(args.destpath, DIRECTORY)
os.chdir(args.destpath)

total_duration = 0

print (f"Boosting " + ("enabled" if args.boost else "disabled"))

print(f"Saving files to {DESTPATH}")
if not os.path.exists(DIRECTORY):
    os.mkdir(DIRECTORY)

i = 1
for pc in PODCASTS:
    parsed = parse(pc['url'], urlopen(pc['url']))
    p = parsed['episodes'].pop(0)
    url = p['enclosures'][0]['url']
    total_duration += p['total_time'] / 60
    print(f"         : {i} out of {len(PODCASTS)}")
    print(f"Title    : {p['title']}")
    print(f"Published: {arrow.get(p['published']).format('ddd DD.MM.YYYY HH:mm')}")
    print(f"Duration : {round(p['total_time'] / 60)}")
    print(f"Info     :\n{p['subtitle']}")

    result = urlparse(url)
    response = urlopen(url)
    _, params = cgi.parse_header(response.headers.get('Content-Disposition', ''))
    filename = params['filename']
    print(f"Saving as: {filename}")

    label_path = os.path.join(TMPPATH, 'label.mp3')

    path = os.path.join(TMPPATH, filename)
    tmppath = os.path.join(TMPPATH, "tmp-" + filename)
    finalpath = os.path.join(DESTPATH, filename)
    if not os.path.exists(finalpath):
        if args.boost:
            urlretrieve(url, path)
            print(f"Compress")
            os.system(f"ffmpeg -hide_banner -loglevel warning -i {path} -filter_complex \"compand=attacks=0:points=-80/-900|-45/-15|-27/-9|0/-7|20/-7:gain=5\" {tmppath}")
        else:
            urlretrieve(url, tmppath)

        # adding label
        tts = gTTS(arrow.utcnow().format('dddd DD.MMMM', locale="de_CH") + f" {pc['name']}. {p['title']}.", lang='de')
        tts.save(label_path)

        cmd = f"ffmpeg -hide_banner -loglevel warning  -i {label_path} -i {tmppath} -filter_complex [0:a][1:a]concat=n=2:v=0:a=1 {finalpath}"
        os.system(cmd)
        os.unlink(tmppath)

    else:
        print(f"{finalpath} already exists. Skipping.")
    print(f"\n")

    i += 1


print(f"Downloaded {round(total_duration)} minutes")

df = shutil.disk_usage(args.destpath)
print(f"{args.destpath} has {round(df.free / 1024 / 1024)}MB free")
