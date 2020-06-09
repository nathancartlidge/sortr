# the music sortr, v0.4
# by infinityio 2019-20

import os
import string
import time

from unidecode import unidecode as deco
from mutagen.easyid3 import EasyID3 as id3
from mutagen.flac import FLAC

directory = 'F:/Music/'
invalidchars = "<>:\"/\\|?*"

count = 0
count2 = 0


def thefolderiser(filename):
    global count, count2

    if filename.endswith(".mp3") or filename.endswith(".flac"):
        if filename.endswith(".flac"): track = FLAC(directory + filename)
        else: track = id3(directory + filename)

        artist = track["artist"][0]
        album  = track["album"][0]
        title  = track["title"][0]

        artist = deco(''.join(c for c in artist if c not in invalidchars))
        album  = deco(''.join(c for c in album  if c not in invalidchars))
        title  = deco(''.join(c for c in title  if c not in invalidchars))

        if filename.endswith(".flac"):
            extension = ".flac"
        else:
            extension = ".mp3"

        if not (os.path.isdir(directory + artist)):
            os.mkdir(directory + artist)
        if not (os.path.isdir(directory + artist + "/" + album)):
            os.mkdir(directory + artist + "/" + album)

        if not os.path.isfile(directory + artist + "/" + album + "/" + title + extension):
            os.rename(directory + filename, directory + artist + "/" + album + "/" + title + extension)

            if   filename.endswith(".mp3")  and os.path.isfile(directory + filename[:-4] + ".lrc"):
                os.rename(directory + filename[:-4] + ".lrc", directory + artist + "/" + album + "/" + title + ".lrc")
            elif filename.endswith(".flac") and os.path.isfile(directory + filename[:-5] + ".lrc"):
                os.rename(directory + filename[:-5] + ".lrc", directory + artist + "/" + album + "/" + title + ".lrc")
                
            count += 1
        else:
            print(title + " already exists in target dir, skipping")
            count2 += 1
        

        # print(filename + " >> " + title + extension)
        print("moved " + str(count) + " files, skipped " + str(count2) + " files    ", end="\r")

def thelyriciser(filename):
    global count, count2
    if filename.endswith(".mp3"): # because of how i am doing lyrics i don't actually need any flacs here?
        if not (os.path.isfile(directory + "lyrics/" + filename[:-4] + ".lrc")):
            return

        track = id3(directory + "lyrics/" + filename)

        artist = track["artist"][0]
        album  = track["album"][0]
        title  = track["title"][0]

        artist = deco(''.join(c for c in artist if c not in invalidchars))
        album  = deco(''.join(c for c in album  if c not in invalidchars))
        title  = deco(''.join(c for c in title  if c not in invalidchars))

        extension = ".lrc"

        if os.path.isfile(directory + artist + "/" + album + "/" + title + extension): # assume lyrics folder is better quality, you may not want this!
            os.remove(directory + artist + "/" + album + "/" + title + extension)

        if os.path.isdir(directory + artist + "/" + album):
            os.rename(directory + "lyrics/" + filename[:-4] + ".lrc", directory + artist + "/" + album + "/" + title + extension)
            count += 1
        else:
            count2 += 1

        # print(filename + " >> " + title + extension)
        print("moved " + str(count) + " files, skipped " + str(count2) + " files    ", end="\r")

def thebadlyriciser(filename):
    if (filename.endswith(".lrc")):
        artist = filename.split(" - ")[1]
        song = filename.split(" - ")[2][:-4]
        if (os.path.isdir(directory + artist)):
            result = find(song, directory + artist + "/")
            if len(result) == 0:
                print("no match found! ", end = "")
                print(artist + " / " + song)
            elif len(result) == 1:
                if result[0].endswith(".flac"):
                    newName = result[0][:-5] + ".lrc"
                else:
                    newName = result[0][:-4] + ".lrc"
                if os.path.isfile(newName):
                    os.remove(newName)
                os.rename(directory + "lyrics/" + filename, newName)
                print(directory + "lyrics/" + filename + " >> " + newName)
            else:
                print("multiple matches found! ", end = "")
                print(artist + " / " + song)
        else:
            print("artist folder not found!")
            print(artist + " / " + song) 
        
def find(name, path, precision = 6):
    result = []
    for root, dirs, files in os.walk(path):
        for fname in files:
            if fname.endswith(".mp3") or fname.endswith(".flac"):
                if fname[:precision] == name[:precision]:
                    # print(fname)
                    result.append(os.path.join(root, fname))

    return result

def thelyricimprover():
    count = 0
    for root, dirs, files in os.walk("F:/Music/"):
        for name in files:
            if name.endswith(".lrc"):
                with open(os.path.join(root, name), "r+") as f:
                    new_f = f.readlines()
                    f.seek(0)
                    for line in new_f:
                        if len(line.strip("\n")) == 10 and line[9] == "]": # timestamp only in line
                            count += 1
                            # f.write(line)
                            # print(os.path.join(root, name))
                            print(str(count) + " lines removed", end = "\r")
                        else:
                            f.write(line)
                    f.truncate()
    print(str(count) + " lines removed", end = "\r")

def deletebadlyrics():
    count = 0
    err = 0

    for root, dirs, files in os.walk("F:/Music/lyrics/test/"):
        for name in files:
            if name.endswith(".lrc"):           
                f = open(os.path.join(root, name), "r")   
                try:
                    test = int(f.readline()[4:6])
                    count += 1
                except ValueError:
                    f.close()
                    os.remove(os.path.join(root, name))
                    print("deleted lyrics at " + root + name, end=" ")
                    err += 1

    print(str(count) + " / " + str(err))

def countlyrics():
    nolyr = 0
    lyr = 0
    f = open("lyrics/nolyr.txt", "w")

    for root, dirs, files in os.walk("F:/Music/"):
        for name in files:
            if name.endswith(".flac"):     
                track = FLAC(os.path.join(root, name))   
                if not os.path.isfile(os.path.join(root, name[:-5] + ".lrc")):
                    nolyr += 1
                    artist = track["artist"][0]
                    album  = track["album"][0]
                    title  = track["title"][0]
                    f.write(artist + " - " + album + " - " + title + "\n")
                else:
                    lyr += 1
            elif name.endswith(".mp3"):
                track = id3(os.path.join(root, name))
                if not os.path.isfile(os.path.join(root, name[:-4] + ".lrc")):
                    artist = track["artist"][0]
                    album  = track["album"][0]
                    title  = track["title"][0]
                    f.write(artist + " - " + album + " - " + title + "\n")
                    nolyr += 1
                else:
                    lyr += 1

    print(str(lyr) + "with lyrics, " + str(nolyr) + " without")
    print(str(round(100 * lyr / (nolyr + lyr), 1)) + "% with lyrics")
    f.close()


if __name__ == "__main__":
    print("\nthe music sortr: it may be inefficient but it works and that's enough for me")
    print(  "this will only sort flacs/mp3s because i don't have any other formats, sorry\n")
    print(  "thank you to the people at mutagen for letting this program read id3 data\n")

    changedir = input("Do you want to change directory from default (" + directory + ")? (y/N) ")
    if changedir == "Y":
        directory = input("Pick a directory: ")

    print("pick a mode:")
    print("1: move files in root dir only")
    print("2: flatten then move all files")
    print("3: only move lyrics across")
    print("4: vaguely fuzzy lyrics matching")
    print("5: count missing lyrics")
    print("6: delete bad lyrics")
    print("7: improve lyrics")

    mode = int(input("> "))
    if mode < 1 or mode > 7:
        mode = 1

    print()

    if os.path.isdir(directory):
        if mode == 1: # boring mode
            for name in os.listdir(directory):
                thefolderiser(name)
            print()

        elif mode == 2: # the flattener
            for root, dirs, files in os.walk(directory): # iterates through all things in all bits of the folder
                for name in files:
                    pathwF = os.path.join(root, name) # get path of file in folder
                    path = os.path.dirname(name) # get path of folder
                    if path != directory: # if not in root directory
                        if name.endswith(".mp3") or name.endswith(".flac"):
                            if os.path.isfile(directory + name): # if file already exists in rootdir, change name
                                if name.endswith(".flac"):
                                    newname = name[:-5] + "_" + ".flac"
                                elif name.endswith(".mp3"):
                                    newname = name[:-4] + "_" + ".mp3"
                            else: # file does not exist in rootdir, no changes to name needed
                                newName = name
                            os.rename(pathwF, directory + name) # will hopefully flatten everything?
                            thefolderiser(name)
            print()
        
        elif mode == 3: # lyrics mode
            for name in os.listdir(directory + "lyrics/"):
                thelyriciser(name)
            print()

        elif mode == 4: # fuzzy lyrics mode
            for name in os.listdir(directory + "lyrics/"):
                thebadlyriciser(name)
            print()
        
        elif mode == 5:
            countlyrics()
            print()

        elif mode == 6:
            deletebadlyrics()
            print()

        elif mode == 7:
            thelyricimprover()
            print()

    else: 
        print("Invalid directory!")