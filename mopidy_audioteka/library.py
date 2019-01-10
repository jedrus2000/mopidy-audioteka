from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy.models import Album, Artist, Ref, SearchResult, Track

from mopidy_audioteka.translator import album_to_ref, artist_to_ref, track_to_ref

logger = logging.getLogger(__name__)


class AudiotekaLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri='audioteka:directory', name='My shelf @ Audioteka')

    def __init__(self, *args, **kwargs):
        super(AudiotekaLibraryProvider, self).__init__(*args, **kwargs)

        # tracks, albums, and artists here refer to what is explicitly
        # in our library.
        self.tracks = {}
        self.albums = {}
        self.artists = {}

        # Setup the root of library browsing.
        self._root = [
            Ref.directory(uri='audioteka:album', name='Books'),
            Ref.directory(uri='audioteka:artist', name='Authors'),
        ]

    def browse(self, uri):
        logger.debug('browse: %s', str(uri))
        if not uri:
            return []
        if uri == self.root_directory.uri:
            return self._root

        parts = uri.split(':')

        # chapters
        if uri == 'audioteka:track':
            return self._browse_tracks()

        # books
        if uri == 'audioteka:album':
            return self._browse_albums()
        
        # a single book
        # uri == 'audioteka:album:album_id'
        if len(parts) == 4 and parts[1] == 'album':
            return self._browse_album(uri)

        # authors
        if uri == 'audioteka:artist':
            return self._browse_artists()

        # a single author
        # uri == 'audioteka:artist:artist_id'
        if len(parts) == 3 and parts[1] == 'artist':
            return self._browse_artist(uri)

        logger.debug('Unknown uri for browse request: %s', uri)
        return []

    def lookup(self, uri):
        logger.debug('lookup: %s', str(uri))
        if uri.startswith('audioteka:track:'):
            return self._lookup_track(uri)
        elif uri.startswith('audioteka:album:'):
            return self._lookup_album(uri)
        elif uri.startswith('audioteka:artist:'):
            return self._lookup_artist(uri)
        else:
            return []

    def refresh(self, uri=None):
        logger.debug('refresh: %s', str(uri))

        self.tracks = {}
        self.albums = {}
        self.artists = {}

        for album, tracks in self.backend.audioteka.get_albums():
            self.artists.update({artist.uri: artist for artist in album.artists})
            self.albums[album.uri] = album
            self.tracks.update({track.uri: track for track in tracks})

    def search(self, query=None, uris=None, exact=False):
        # TODO
        logger.debug('search: query=%s, uris=%s, exact=%s ' % (query, uris, exact) )
        # search - query={u'any': [u'test']}, uris=[u'audioteka:album'], exact=False
        return SearchResult(uri='audioteka:search',
                            tracks=[],
                            artists=[],
                            albums=[])

    def _browse_tracks(self):
        logger.debug('browse tracks')
        tracks = list(self.tracks.values())
        tracks.sort(key=lambda ref: ref.name)
        refs = []
        for track in tracks:
            refs.append(track_to_ref(track))
        return refs

    def _browse_albums(self):
        logger.debug('browse albums')
        refs = []
        for album in self.albums.values():
            refs.append(album_to_ref(album))
        refs.sort(key=lambda ref: ref.name)
        return refs

    def _browse_album(self, uri):
        logger.debug('browse album: uri=%s', str(uri))
        refs = []
        for track in self._lookup_album(uri):
            refs.append(track_to_ref(track, True))
        return refs

    def _browse_artists(self):
        logger.debug('browse artists')
        refs = []
        for artist in self.artists.values():
            refs.append(artist_to_ref(artist))
        refs.sort(key=lambda ref: ref.name)
        return refs

    def _browse_artist(self, uri):
        # browse: audioteka:artist:390afd6876147086cf9e3720b9cb562c
        logger.debug('browse artist: uri=%s', str(uri))
        refs = []
        for album in self._get_artist_albums(uri):
            refs.append(album_to_ref(album))
            refs.sort(key=lambda ref: ref.name)
        return refs

    def _lookup_track(self, uri):
        logger.debug('lookup track: uri=%s', str(uri))
        try:
            return [self.tracks[uri]]
        except KeyError:
            logger.debug('Track not a library track %r', uri)
            return []

    def _lookup_album(self, uri):
        logger.debug('lookup album: uri=%s', str(uri))
        try:
            album = self.albums[uri]
        except KeyError:
            logger.debug('Failed to lookup %r', uri)
            return []

        return sorted([track for track in self.tracks.values() if track.album == album],
                      key=lambda t: t.track_no)

    def _get_artist_albums(self, uri):
        logger.debug('_get_artist_albums available for artist uri: %s', uri)
        return [album for album in self.albums.values() if uri in [artist.uri for artist in album.artists]]

    def _lookup_artist(self, uri):
        logger.debug('_lookup_artist, uri: %r', uri)
        return self.artists[uri]
