"""
Simple tool to help organize my personal music library.

Copyright (C) 2017, Dave Brookshire <dave@brookshire.org>
"""
import hashlib
import os
import re
import time

import eyed3

debug = False


class CollatorFile():
    """
    Abstraction of individual files in library collection, using fields in the actual name of the files
    and certain ID3 tags to attempt to normalize the formatting and organization of the library.
    """
    fname = None
    hash = None

    def __init__(self, fname):
        self.fname = fname
        self.hash = self.generate_hash()
        self.audiofile = eyed3.load(self.fname)

    def __str__(self):
        ret = "Title: {0}, Artist: {1}, Album: {2}".format(os.path.basename(self.fname),
                                                           self.path_artist,
                                                           self.path_album)
        ret += "\nTitle Tag: {0}".format(self.title_tag)
        ret += "\nAlbum Tag: {0}".format(self.album_tag)
        ret += "\nArtist Tag: {0}".format(self.artist_tag)
        return ret

    @property
    def title_tag(self):
        """
        Lookup the ID3 Title tag value.
        :return: 
        """
        title_tag = None
        try:
            title_tag = self.audiofile.tag.title
        except AttributeError:
            pass
        return title_tag

    @property
    def album_tag(self):
        """
        Lookup the ID3 Album tag value.
        :return: 
        """
        album_tag = None
        try:
            album_tag = self.audiofile.tag.album
        except AttributeError:
            pass
        return album_tag

    @property
    def artist_tag(self):
        """
        Lookup the ID3 Artist tag value.
        :return: 
        """
        artist_tag = None
        try:
            artist_tag = self.audiofile.tag.artist
        except AttributeError:
            pass
        return artist_tag

    def generate_hash(self):
        """
        Generate SHA1 hash value for the file.  We'll use this to uniquely identify files and help
        determine duplicates.
        :return: 
        """
        BLOCKSIZE = 65536
        hasher = hashlib.sha1()
        with open(self.fname, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()

    def is_audio_file(self):
        """
        Determine if the file is an audio file or not.  Right now, this is based soley on the extension
        of the file name.
        :return: 
        """
        ret = False
        iaf_re = re.compile(".+\.(mp3|m4a)$", re.IGNORECASE)
        mo = iaf_re.match(os.path.basename(self.fname))
        if (mo):
            ret = True

        return ret

    def path_elements(self):
        return self.fname.split('/')

    @property
    def path_artist(self):
        return self.path_elements()[4]

    @property
    def path_album(self):
        return self.path_elements()[5]


def build_library(path):
    """
    Recursively build a library of audio files given a directory path.
    :param path: 
    :param debug: 
    :return: 
    """
    library = []
    unknowns = []

    if debug:
        print("Finding audio files in {0}".format(path))

    found = os.listdir(path)
    for f in found:
        fpath = os.path.join(path, f).replace("\\", "/")
        if os.path.isdir(fpath):
            l, u = build_library(fpath)
            library.extend(l)
            unknowns.extend(u)
        elif os.path.isfile(fpath):
            ncf = CollatorFile(fpath)
            if ncf.is_audio_file():
                library.append(ncf)
            else:
                unknowns.append(fpath)
        else:
            unknowns.append(fpath)

    if debug:
        print("Found {0} audio files, and {1} unknown files".format(len(library),
                                                                    len(unknowns)))

    return library, unknowns


if __name__ == '__main__':
    start = time.time()
    library, unknowns = build_library("/home/ec2-user/dev.music")
    stop = time.time()

    print("Processed library in {0} seconds".format(stop - start))
    print("Library consists of {0} discovered and identified audio files".format(len(library)))
    print("Found {0} unknown or unidentifiable files".format(len(unknowns)))

    for t in library:
        print(t)

    if unknowns and debug:
        print("\n\nUnknown Files")
        print("-------------")
        for u in unknowns:
            print("  {0}".format(u))
