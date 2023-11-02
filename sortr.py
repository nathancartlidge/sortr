#!/usr/bin/env python
# the music sortr, v0.5
# by infinityio 2019-21

import os
import console_interface
import helper_functions

if os.name == "nt":
    directory = os.getcwd() + "\\"
else:
    directory = os.getcwd() + "/"

choice = console_interface.get_option(
    title="sortr",
    subtitle=f"(Current Directory: {directory})",
    options=[
        "move music files in root directory",
        "flatten all music files to root directory",
        "attempt to fix lyrics files",
        "load playlist (from plex)",
        "re-transcode playlist"
    ]
)

if choice == 0: # move music files in root
    for name in os.listdir(directory):
        helper_functions.song_into_folder(directory, name)
elif choice == 1: # flatten
    helper_functions.flatten_all_files(directory)
elif choice == 2: # fix lyrics
    count = 0
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.endswith(".lrc"):
                result = helper_functions.lyric_gap_fixer(os.path.join(root, name), threshold=3)
                if not result:
                    count += 1
    print(f"{count} files changed")
elif choice == 3: # load playlist
    url = console_interface.get_input(title="Enter your plex server URL")
    token = console_interface.get_input(title="Enter your Plex access token")
    songs = helper_functions.select_playlist(url=url, token=token)
    helper_functions.make_playlist_copy(directory, songs)
    quality = console_interface.get_input(title="Choose a quality (0-4 recommended)")
    helper_functions.convert_playlist(directory, quality=quality)
elif choice == 4:
    quality = console_interface.get_input(title="Choose a quality (0-4 recommended)")
    helper_functions.convert_playlist(directory, quality=quality)
else:
    raise NotImplementedError