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
            Ref.directory(uri='audioteka:artist', name='Authors/Readers'),
            # Ref.directory(uri='audioteka:track', name='Chapters')
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
        logger.debug('search - query=%s, uris=%s, exact=%s ' % (query, uris, exact) )
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
        logger.debug('browse album, uri: %s', str(uri))
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
        logger.debug('browse artist, uri: %s', str(uri))
        refs = []
        for album in self._get_artist_albums(uri):
            refs.append(album_to_ref(album))
            refs.sort(key=lambda ref: ref.name)
        if len(refs) > 0:
            refs.insert(0, Ref.directory(uri=uri + ':all', name='All Tracks'))
            is_all_access = uri.startswith('audioteka:artist:A')
            if is_all_access:
                refs.insert(1, Ref.directory(uri=uri + ':top', name='Top Tracks'))
            return refs
        else:
            # Show all tracks if no album is available
            return self._browse_artist_all_tracks(uri)

    def _lookup_track(self, uri):
        logger.debug('lookup track, uri: %s', str(uri))
        try:
            return [self.tracks[uri]]
        except KeyError:
            logger.debug('Track not a library track %r', uri)
            return []

    def _lookup_album(self, uri):
        logger.debug('lookup album, uri: %s', str(uri))
        try:
            album = self.albums[uri]
        except KeyError:
            logger.debug('Failed to lookup %r', uri)
            return []

        return sorted([track for track in self.tracks.values() if track.album == album],
                      key=lambda t: t.track_no)
        # tracks = self._find_exact(
        #    dict(album=album.name,
        #         artist=[artist.name for artist in album.artists],
        #         date=album.date)).tracks
        # return sorted(tracks, key=lambda t: (t.disc_no, t.track_no))

    def _get_artist_albums(self, uri):
        logger.debug('0 albums available for artist %r', uri)
        return []

    def _lookup_artist(self, uri, exact_match=False):
        logger.debug('_lookup_artist, uri: %r', uri)
        return []

    """
    def _lookup_artist(self, uri, exact_match=False):
        def sorter(track):
            return (
                track.album.date,
                track.album.name,
                track.disc_no,
                track.track_no,
            )

        if self.all_access:
            try:
                all_access_id = self.aa_artists[uri.split(':')[2]]
                artist_infos = self.backend.session.get_artist_info(
                    all_access_id, max_top_tracks=0, max_rel_artist=0)
                if not artist_infos or not artist_infos['albums']:
                    logger.warning('Failed to lookup %r', artist_infos)
                tracks = [
                    self._lookup_album('gmusic:album:' + album['albumId'])
                    for album in artist_infos['albums']]
                tracks = reduce(lambda a, b: (a + b), tracks)
                return sorted(tracks, key=sorter)
            except KeyError:
                pass
        try:
            artist = self.artists[uri]
        except KeyError:
            logger.debug('Failed to lookup %r', uri)
            return []

        tracks = self._find_exact(
            dict(artist=artist.name)).tracks
        if exact_match:
            tracks = filter(lambda t: artist in t.artists, tracks)
        return sorted(tracks, key=sorter)
   
    def _find_exact(self, query=None, uris=None):
        # Find exact can only be done on gmusic library,
        # since one can't filter all access searches
        lib_tracks, lib_artists, lib_albums = self._search_library(query, uris)

        return SearchResult(uri='audioteka:search',
                            tracks=lib_tracks,
                            artists=lib_artists,
                            albums=lib_albums)

    def _search(self, query=None, uris=None):
        return [], [], []

    def _search_library(self, query=None, uris=None):
        return [], [], []

    def _validate_query(self, query):
        for (_, values) in query.iteritems():
            if not values:
                raise LookupError('Missing query')
            for value in values:
                if not value:
                    raise LookupError('Missing query')

    def _to_mopidy_track(self, song):
        track_id = song.get('id', song.get('nid'))
        if track_id is None:
            raise ValueError
        if track_id[0] != "T" and "-" not in track_id:
            track_id = "T"+track_id
        return Track(
            uri='gmusic:track:' + track_id,
            name=song['title'],
            artists=[self._to_mopidy_artist(song)],
            album=self._to_mopidy_album(song),
            track_no=song.get('trackNumber', 1),
            disc_no=song.get('discNumber', 1),
            date=unicode(song.get('year', 0)),
            length=int(song['durationMillis']),
            bitrate=320)

    def _to_mopidy_album(self, song):
        name = song.get('album', '')
        artist = self._to_mopidy_album_artist(song)
        date = unicode(song.get('year', 0))

        album_id = song.get('albumId')
        if album_id is None:
            album_id = create_id(artist.name + name + date)

        uri = 'gmusic:album:' + album_id
        images = get_images(song)
        return Album(
            uri=uri,
            name=name,
            artists=[artist],
            num_tracks=song.get('totalTrackCount'),
            num_discs=song.get('totalDiscCount'),
            date=date,
            images=images)

    def _to_mopidy_artist(self, song):
        name = song.get('artist', '')
        artist_id = song.get('artistId')
        if artist_id is not None:
            artist_id = artist_id[0]
        else:
            artist_id = create_id(name)
        uri = 'gmusic:artist:' + artist_id
        return Artist(uri=uri, name=name)

    def _to_mopidy_album_artist(self, song):
        name = song.get('albumArtist', '')
        if name.strip() == '':
            name = song.get('artist', '')
        uri = 'gmusic:artist:' + create_id(name)
        return Artist(uri=uri, name=name)

    def _aa_search_track_to_mopidy_track(self, search_track):
        track = search_track['track']

        aa_artist_id = create_id(track['artist'])
        if 'artistId' in track:
            aa_artist_id = track['artistId'][0]
        else:
            logger.warning('No artistId for Track %r', track)

        artist = Artist(
            uri='gmusic:artist:' + aa_artist_id,
            name=track['artist'])

        album = Album(
            uri='gmusic:album:' + track['albumId'],
            name=track['album'],
            artists=[artist],
            date=unicode(track.get('year', 0)))

        return Track(
            uri='gmusic:track:' + track['storeId'],
            name=track['title'],
            artists=[artist],
            album=album,
            track_no=track.get('trackNumber', 1),
            disc_no=track.get('discNumber', 1),
            date=unicode(track.get('year', 0)),
            length=int(track['durationMillis']),
            bitrate=320)

    def _aa_search_artist_to_mopidy_artist(self, search_artist):
        artist = search_artist['artist']
        uri = 'gmusic:artist:' + artist['artistId']
        return Artist(uri=uri, name=artist['name'])

    def _aa_search_album_to_mopidy_album(self, search_album):
        album = search_album['album']
        uri = 'gmusic:album:' + album['albumId']
        name = album['name']
        artist = self._aa_search_artist_album_to_mopidy_artist_album(album)
        date = unicode(album.get('year', 0))
        return Album(
            uri=uri,
            name=name,
            artists=[artist],
            date=date)

    def _aa_search_artist_album_to_mopidy_artist_album(self, album):
        name = album.get('albumArtist', '')
        if name.strip() == '':
            name = album.get('artist', '')
        uri = 'gmusic:artist:' + create_id(name)
        return Artist(uri=uri, name=name)

    def _convert_to_int(self, string):
        try:
            return int(string)
        except ValueError:
            return object()
    """
