# sortr
A python script to categorise ID3-tagged music (such as that obtained from ripped CDs) into folders based upon the metadata provided.

> This was hacked together for my own personal use and has not been updated in many years - as such, it may not work anymore (although it might be a good starting point for a similar project in future)

Built using Mutagen, a library for extracting ID3 data.

## usage

- Modify the directory to where your music is stored
- Run the script, selecting a mode from below:

### modes
1. Will move all flac / mp3 files from the root directory only, into folder by artist then album (if it sees any associated lyric files it will move them too)
2. Will pull every flac and mp3 file from its current hiding place inside the folder chosen, and then run mode 1. note that this does not like lyrics yet, although that may come in the future
3. A special use case: if you have synced lyric files and put them in a folder called lyrics in the root directory, it will try and match these to their songs
4. A modification of mode 3 that cares less about titles (ie only reads the first few characters of albums etc)
5. Will tell you all the songs that haven't found a lyric friend yet
6. eats lyrics that don't seem to be properly synced
7. is very obscure but it makes lyrics with blank lines with timecodes not have blank lines with timecodes so that some music players (eg Plex) can understand the lyrics properly

enjoy!
