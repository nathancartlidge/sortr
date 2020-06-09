# sortr
A small, approximately lightweight music sorter that works by reading id3 data and using it to folderise songs

## usage

place the script at the top level folder where your music sits
run it however you please, although note you may need some modules first (it uses mutagen and unidecode)

## modes
```
mode 1 will move all flac / mp3 files from the root directory only, into folder by artist then album
       (if it sees any associated lyric files it will move them too)

mode 2 will pull every flac and mp3 file from its current hiding place inside the folder chosen and
       run mode 1. note that this does not like lyrics yet, although that may come in the future

mode 3 is a special use case, but if you happen to coincidentally find some synced lyric files from a
       completely legal source and put them in a folder called lyrics in the root dir it will try and
       find some songs that go along with those files

mode 4 is mode 3 but cares less about titles (ie only reads the first few characters of albums etc)

mode 5 will tell you all the songs that haven't found a lyric friend yet

mode 6 eats lyrics that don't seem to be properly synced

mode 7 is very obscure but it makes lyrics with blank lines with timecodes not have blank lines with
       timecodes so that some music players can understand the lyrics properly
```

enjoy!
