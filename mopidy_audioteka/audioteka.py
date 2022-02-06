import requests
import logging
from datetime import datetime
import time

from audtekapi import AudiotekaAPI
from mopidy import httpclient
from mopidy.models import Album, Artist, Track, fields
from mopidy_audioteka.translator import create_id
from mopidy_audioteka.exceptions import exception_guard

logger = logging.getLogger(__name__)


class Audioteka:
    def __init__(self, proxy, username, password, device_id):
        self._api: AudiotekaAPI = AudiotekaAPI(username, password, device_id)
        proxy_formatted = httpclient.format_proxy(proxy)
        if proxy_formatted:
            self._api.session.proxies.update({'http': proxy_formatted, 'https': proxy_formatted})
            self._api.session.verify = False

        self._download_server_address = ''
        self._download_url_footer = ''

    @exception_guard
    def get_albums_with_tracks(self, no_of_cached=0):
        retrieved_audiobooks: int = 0
        _raw = self._api.get_shelf()
        if no_of_cached == _raw['total']:
            logger.debug('No of cached books same as found online. Skipping retrieving more data.')
            return
        while retrieved_audiobooks < _raw['total']:
            for _product in _raw['_embedded']['app:product']:
                retrieved_audiobooks += 1
                chapters = self._get_chapters(_product['id'])
                album = Album(
                    uri=album_uri_encode(_product['id']),
                    name=_product['name'],
                    artists=self._get_artists(_product['description']),
                    num_tracks=len(chapters),
                    num_discs=1)
                tracks = self._get_tracks(album, chapters)
                yield album, tracks, _product['image_url']
            _raw = self._api.get_shelf(_raw['page']+1)

    def _get_tracks(self, album, chapters=None):
        audiobook_id = album.uri.split(':')[2]
        if not chapters:
            chapters = self._get_chapters(audiobook_id)

        return [
            AudiotekaTrack(
                uri=track_uri_encode(audiobook_id, chapter['id'], chapter['index']+1,
                                     chapter['_links']['app:stream']['href']),
                name=chapter['title'],
                artists=album.artists,
                album=album,
                genre='Audiobook',
                track_no=chapter['index']+1,
                disc_no=1,
                date=album.date,
                length=chapter['duration'],
                file_size=chapter['size'],
                last_modified=int(time.mktime(datetime.now().timetuple()) * 1000)
            ) for chapter in chapters
        ]

    def _get_artists(self, names: str):
        artists_names = list()
        artists_names += [s.strip() for s in names.split(',')]
        return [Artist(uri='audioteka:artist:' + create_id(name), name=name) for name in artists_names]

    @exception_guard
    def get_stream_url(self, track):
        if isinstance(track, dict):
            track_uri_decoded = track
        else:
            track_uri_decoded = track_uri_decode(track)
        logger.debug(f"get_stream_url - getting url for track link: {track_uri_decoded['track_link']}")
        track_file_data = self._api.get_track(track_uri_decoded['track_link'])
        return track_file_data['url']

    def _get_chapters(self, audiobook_id):
        return self._api.get_audiobook_track_list(audiobook_id)['_embedded']['app:track']


def track_uri_decode(track_uri):
    track_values = track_uri.split(':')
    return {
        'audiobook_id': track_values[2],
        'track_id': track_values[3],
        'track_no': track_values[4],
        'track_link': track_values[5]
    }


def track_uri_encode(audiobook_id, track_id, track_no, track_link):
    return f'audioteka:track:{audiobook_id}:{track_id}:{track_no}:{track_link}'


def album_uri_encode(audiobook_id):
    return f'audioteka:album:{audiobook_id}'


class AudiotekaTrack(Track):
    #: The track file size in bytes. Read-only.
    file_size = fields.Integer(min=0)

