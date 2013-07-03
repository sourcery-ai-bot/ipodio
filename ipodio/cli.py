# -*- coding: utf-8 -*-

import re
import os
import sys
import shutil

import ipodio

from manager import Manager


manager = Manager()


def first(collection):
    for element in collection:
        return element


def error(message):
    print('Error: ' + message)
    sys.exit(1)


def _sorted_tracks(tracks, key=None):
    def by(field):
        def accessor(element):
            return (key(element) if key else element).internal[field]
        return accessor

    tracks.sort(key=by('track_nr'))
    tracks.sort(key=by('album'))
    tracks.sort(key=by('artist'))

    return tracks


def _line(data):
    title = data['title'] or ''
    album = data['album'] or ''
    artist = data['artist'] or ''

    return "{title:30}  {album:30}  {artist:18}".format(
        title=title[:30], album=album[:30], artist=artist[:18])


def _compile_regular_expression(expression):
    try:
        return re.compile(expression, flags=re.IGNORECASE)
    except (ValueError, TypeError, re.error):
        error('Invalid expression "{}"'.format(expression))


def _filter_by_regular_expression(regexp, tracks):
    return [track for track in tracks if regexp.search(_line(track.internal))]


@manager.command
def list(mountpoint, expression):
    """List ipod contents"""
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    regexp = _compile_regular_expression(expression)
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    if tracks:
        print(_line(dict(title='Title', album='Album', artist='Artist')))
        print('-' * 80)

    for track in _sorted_tracks(tracks):
        print(_line(track.internal))

    if database.updated:
        database.save()


@manager.command
def duplicates(mountpoint):
    """List ipod contents grouping duplicated tracks"""
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    track_groups = _sorted_tracks(database.duplicates, key=lambda g: first(g))

    if track_groups:
        print(_line(dict(title='Title', album='Album', artist='Artist')))
        print('-' * 80)

    for group in track_groups:
        for track in group:
            print(_line(track.internal))

    if database.updated:
        database.save()


@manager.command
def push(mountpoint, filename):
    """List ipod contents grouping duplicated tracks"""
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    track = ipodio.database.Track.create(filename)

    if database.get(track):
        return '{} already in the ipod'.format(track.internal)

    database.add(track)
    database.copy_files()
    database.save()


@manager.command
def pull(mountpoint, expression):
    """List ipod contents grouping duplicated tracks"""
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    destination = '.'

    regexp = _compile_regular_expression(expression)
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    for track in tracks:
        track_name = u'{track_nr}_{title}_{album}_{artist}'.format(
            track_nr=track.internal['track_nr'],
            title=track.internal['title'],
            album=track.internal['album'],
            artist=track.internal['artist']
        )

        print(track.internal, track_name)
        shutil.copy(track.filename, os.path.join(destination, track_name))


@manager.command
def rm(mountpoint, expression):
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    print(_line(dict(title='Title', album='Album', artist='Artist')))
    print('-' * 80)

    regexp = _compile_regular_expression(expression)
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    for track in tracks:
        print(_line(track.internal))
        database.remove(track)

    if database.updated:
        database.save()


@manager.command
def rename(mountpoint, expression, replacement):
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    regexp = _compile_regular_expression(expression)
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    for track in tracks:
        track.internal['artist'] = regexp.sub(replacement, track.internal['artist'])
        track.internal['album'] = regexp.sub(replacement, track.internal['album'])
        track.internal['title'] = regexp.sub(replacement, track.internal['title'])

        print(_line(track.internal))

    if tracks:
        database.save()


def main():
    manager.main()


if __name__ == '__main__':
    main()
