from multiprocessing.pool import ThreadPool
import re
import os
import html
import time
import shutil
import datetime
import subprocess
from typing import Union
import urllib.request

from math import floor

from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from unidecode import unidecode

import console_interface

PLAYLIST_MATCHER = re.compile(b'Playlist.*key="(.*?)".*title="(.*?)"')
TIMESTAMP_MATCHER = re.compile("\[\d\d:\d\d\.\d\d\]")
TIME_MATCHER = re.compile("\[(\d\d):(\d\d)\.(\d\d)\]")
SONG_MATCHER = re.compile(b'file="(.*?)"')

INVALID_CHARS = "<>:\"/\\|?*"

def get_safe_name(track: Union[FLAC, EasyID3]):
    artist = track["artist"][0]
    album  = track["album"][0]
    title  = track["title"][0]

    artist = ''.join(c for c in unidecode(artist) if c not in INVALID_CHARS).strip()
    album  = ''.join(c for c in unidecode(album)  if c not in INVALID_CHARS).strip()
    title  = ''.join(c for c in unidecode(title)  if c not in INVALID_CHARS).strip()

    return artist, album, title

def make_path(directory, artist, album):
    if not (os.path.isdir(directory + artist)):
        os.mkdir(directory + artist)
    if not (os.path.isdir(directory + artist + "/" + album)):
        os.mkdir(directory + artist + "/" + album)

def move_file(directory, filename, artist, album, title, extension, move_lyrics=True, replace_mp3=True):
    if os.path.isfile(directory + artist + "/" + album + "/" + title + extension):
        return False
    
    os.rename(directory + filename + extension,  directory + artist + "/" + album + "/" + title + extension)
    
    try:
        if move_lyrics and os.path.isfile(directory + filename + ".lrc"):
            os.rename(directory + filename + ".lrc", directory + artist + "/" + album + "/" + title + ".lrc")
    except FileExistsError:
        print(f"Ignoring new lyrics file for {title}")
        os.remove(directory + filename + ".lrc")

    if extension == ".flac" and replace_mp3 and os.path.isfile(directory + artist + "/" + album + "/" + title + ".mp3"):
        os.remove(directory + artist + "/" + album + "/" + title + ".mp3")

def song_into_folder(directory, filename):
    if filename.endswith(".mp3") or filename.endswith(".flac"):
        if filename.endswith(".flac"): track = FLAC(directory + filename)
        else: track = EasyID3(directory + filename)

        artist, album, title = get_safe_name(track)

        if filename.endswith(".flac"):
            filename = filename[:-5]
            extension = ".flac"
        else:
            filename = filename[:-4]
            extension = ".mp3"

        make_path(directory, artist, album)

        result = move_file(directory, filename, artist, album, title, extension)
        return result

def move_files_in_root_dir(directory):
    failure_count = 0
    success_count = 0
    for name in os.listdir(directory):
        result = song_into_folder(directory, name)
        if result:
            success_count += 1
        else:
            failure_count += 1
    print(f"{success_count} moved, {failure_count} failed")

def flatten_all_files(directory):
    for root, _, files in os.walk(directory): # iterates through all things in all bits of the folder
        for name in files:
            pathwF = os.path.join(root, name) # get path of file in folder
            path = os.path.dirname(name) # get path of folder
            if path != directory: # if not in root directory
                if name.endswith(".mp3"):
                    filename = name[:-4]
                    extension = ".mp3"
                elif name.endswith(".flac"):
                    filename = name[:-5]
                    extension = ".flac"
                else:
                    continue

                new_filename = filename
                while os.path.isfile(directory + new_filename + extension):
                    new_filename += "_"
                    
                os.rename(pathwF, directory + new_filename + extension) # will hopefully flatten everything?

                if os.path.isfile(path + "/" + filename + ".lrc"):
                    os.rename(path + "/" + filename + ".lrc", directory + new_filename + ".lrc")

def lyric_gap_fixer(file, keep_meta=True, threshold=5):
    with open(file, "r", encoding="utf-8") as lyrics_file:
        input_lines = lyrics_file.readlines()

    line_maker = lambda t: f"[{floor(t.seconds / 60):02}:{t.seconds % 60:02}.{floor(t.microseconds/10000):02}]\n"

    last_time = None
    blank_line = None
    output_lines = []

    for line in input_lines:
        if timestamp := TIMESTAMP_MATCHER.match(line):
            mins, secs, csecs = map(int, TIME_MATCHER.findall(timestamp.group())[0])
            time = datetime.timedelta(minutes=mins, seconds=secs, microseconds=csecs*10000)
            if len(line) == 11:
                if time == last_time:
                    blank_line = time
                else:
                    output_lines.append(line)
            else:
                if blank_line:
                    new_time = min(time, blank_line + datetime.timedelta(seconds=threshold))
                    output_lines.append(line_maker(new_time))
                    blank_line = None
                output_lines.append(line)
                last_time = time

        elif keep_meta: # keep metadata
            output_lines.append(line)

    with open(file, "w", encoding="utf-8") as lyrics_file:
        lyrics_file.writelines(output_lines)
    
    return output_lines == input_lines


def get_playlists(url, token):
    playlists_url = f"{url}/playlists?X-Plex-Token={token}"
    with urllib.request.urlopen(playlists_url) as response:
        xml = response.read()

    return [(html.unescape(a.decode('utf-8')), html.unescape(b.decode('utf-8')))
            for a, b in PLAYLIST_MATCHER.findall(xml)]

def select_playlist(url, token, index=None):
    playlists = get_playlists(url=url, token=token)
    if index is not None:
        selected_index = index
    else:
        selected_index = console_interface.get_option(
            title="Select a playlist to download",
            options=[x[1] for x in playlists]
        )
    selected_playlist = playlists[selected_index][0]
    
    playlists_url = f"{url}{selected_playlist}?X-Plex-Token={token}"
    with urllib.request.urlopen(playlists_url) as response:
        xml = response.read()
    
    return [html.unescape(x.decode('utf-8'))[7:] for x in SONG_MATCHER.findall(xml)]

def make_playlist_copy(directory, songs):
    if os.path.isdir(directory + "sortr/temp/"):
        shutil.rmtree(directory + "sortr/temp/")
        time.sleep(0.5)

    os.makedirs(directory + "sortr/temp/")
    for i, song in enumerate(songs):
        print(f"copying song {i+1} of {len(songs)} ", end="\r")
        title = f"{i:03}_{song.split('/')[-1]}"
        shutil.copy2(directory + song, directory + "sortr/temp/" + title)
    
def convert_playlist(directory, quality=2, threads=None):
    if not os.path.isdir(directory + "sortr/temp/"):
        return False

    if os.path.isdir(directory + "sortr/output/"):
        shutil.rmtree(directory + "sortr/output/")
        time.sleep(0.5)

    os.makedirs(directory + "sortr/output/")
    
    jobs = []
    for file in os.listdir(directory + "sortr/temp/"):
        file_as_mp3 = file[:-5] + ".mp3" if file.endswith(".flac") else file
        jobs.append([f"{directory}/sortr/ffmpeg", '-loglevel', 'error', '-i', f"sortr/temp/{file}", '-map', '0:a', '-codec:a', 'libmp3lame', '-qscale:a', f'{quality}', f"sortr/output/{file_as_mp3}"])

    def transcode(work):
        subprocess.run(work, stdout=subprocess.DEVNULL)

    pool = ThreadPool(threads)
    for i, _ in enumerate(pool.imap_unordered(transcode, jobs)):
        print(f"file {i+1} of {len(jobs)}", end="\r")

    pool.close()
    pool.join()

    return True
