#!/usr/bin/env python3

import sys
import glob
import os.path
import mutagen
from mutagen.mp4 import MP4, MP4Cover
from termcolor import colored
import xml.etree.ElementTree as etree
from dateutil.parser import parse


def main():
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], '<root-bbc-radio-dir>')
        sys.exit(1)
    if os.path.isdir(sys.argv[1]):
        print('Tagging audio files in', sys.argv[1])
        audio_files = [f for f in glob.iglob(sys.argv[1] + '**/*.m4a',
                                             recursive=True)]
        for track in audio_files:
            write_text_metadata(track)
    else:
        write_text_metadata(sys.argv[1])


def write_text_metadata(track):
    '''Attempts to find an nfo file with metadata and writes the textual tag
    data'''
    metadata = mutagen.File(track)
    if ('\xa9nam' in metadata.keys() and
            '\xa9alb' in metadata.keys() and
            '\xa9ART' in metadata.keys()):
        print(colored('\tAlready tagged: ' + track, 'green'))
        return
    print('Writing metadata for:', track)
    infofile = os.path.splitext(track)[0] + '.xml'
    if not os.path.isfile(infofile):
        print(colored('\tUnable to find metadata file for: ' + infofile, 'red'))
        return
    print(colored('\tReading metadata from ' + infofile, 'green'))
    tree = etree.parse(infofile)
    root = tree.getroot()
    print(colored('\tDescription: ' +
                  root.find('{http://linuxcentre.net/xmlstuff/get_iplayer}desc').text, 'green'))
    date = parse(
        root.find('{http://linuxcentre.net/xmlstuff/get_iplayer}firstbcastdate').text)
    # print(date.isocalendar()[1])
    metadata = MP4(track)
    metadata['\xa9day'] = str(date.year)
    # metadata['\xa9day'] = str(date.strftime('%Y-%m-%d'))
    metadata['trkn'] = [(date.isocalendar()[1], 52)]
    metadata['desc'] = root.find(
        '{http://linuxcentre.net/xmlstuff/get_iplayer}desclong').text
    metadata['aART'] = root.find(
        '{http://linuxcentre.net/xmlstuff/get_iplayer}name').text
    metadata['\xa9alb'] = root.find(
        '{http://linuxcentre.net/xmlstuff/get_iplayer}name').text + ' - ' + str(date.year)
    metadata['\xa9ART'] = root.find(
        '{http://linuxcentre.net/xmlstuff/get_iplayer}episodeshort').text
    metadata['\xa9gen'] = root.find(
        '{http://linuxcentre.net/xmlstuff/get_iplayer}categories').text.split(',')[1]
    metadata['\xa9nam'] = root.find('{http://linuxcentre.net/xmlstuff/get_iplayer}title').text + \
        ' - ' + \
        root.find(
            '{http://linuxcentre.net/xmlstuff/get_iplayer}firstbcastdate').text
    coverfile = os.path.isfile(os.path.splitext(track)[0] + '.jpg')
    if os.path.isfile(coverfile):
        with open(coverfile, 'rb') as file:
            metadata['covr'] = [
                MP4Cover(file.read(), imageformat=MP4Cover.FORMAT_JPEG)]
    metadata.save()


if __name__ == '__main__':
    main()
