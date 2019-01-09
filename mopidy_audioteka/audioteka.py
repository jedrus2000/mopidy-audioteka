# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import logging
from datetime import datetime
import time

import audtekapi as api
from mopidy import httpclient
from mopidy.models import Album, Artist, Ref, SearchResult, Track
from mopidy_audioteka.translator import create_id

logger = logging.getLogger(__name__)


class Audioteka:
    def __init__(self, backend):
        self._backend = backend
        self._session = requests.Session()
        proxy = httpclient.format_proxy(backend.config['proxy'])
        self._session.proxies.update({'http': proxy, 'https': proxy})

        self._credentials = api.login(
            backend.config['audioteka']['username'],
            backend.config['audioteka']['password'], self._session)
        self._download_server_address = ''
        self._download_url_footer = ''

    def get_albums(self, with_tracks=True):
        books = api.get_shelf( self._credentials, self._session)
        logger.debug('books shelf data: %s', str(books))
        self._download_url_footer = books['Footer']
        self._download_server_address = books['ServerAddress']

        for book in books['Books']:
            chapters = self._get_chapters(book['LineItemId'], book['OrderTrackingNumber'])
            album = Album(
                uri=album_uri_encode(book['LineItemId'], book['OrderTrackingNumber']),
                name=book['Title'],
                artists=self.get_artists(book),
                num_tracks=len(chapters),
                images=[book['BigPictureLink']],
                num_discs=1,
                date=api.epoch_to_datetime(book['ProductDateAdd']).strftime('%Y-%m-%d'))
            tracks = self.get_tracks(album, chapters)
            yield album, tracks

    def get_tracks(self, album, chapters=None):
        album_ids = album.uri.split(':')
        if not chapters:
            chapters = self._get_chapters(album_ids[2], album_ids[3])
        try:
            return [
                Track(
                    uri=track_uri_encode(album_ids[2], album_ids[3],
                                         chapter['Track'], chapter['Link']),
                    name=chapter['ChapterTitle'],
                    artists=album.artists,
                    album=album,
                    genre='Audiobook',
                    track_no=chapter['Track'],
                    disc_no=1,
                    date=album.date,
                    length=chapter['Length'],
                    last_modified=int(time.mktime(datetime.now().timetuple()) * 1000)
                ) for chapter in chapters
            ]
        except Exception as e:
            logger.error(str(e)+' Album IDs: %s, Chapters: %s', str(album_ids), str(chapters))

    def get_artists(self, book):
        artists_names = list()
        artists_names += book['Author'].split(';')
        artists_names += book['Reader'].split(';')
        return [Artist(uri='audioteka:artist:' + create_id(name), name=name) for name in artists_names]

    def download_track(self, track):
        if isinstance(track, dict):
            track_uri_decoded = track
        else:
            track_uri_decoded = track_uri_decode(track)

        return api.get_chapter_file(track_uri_decoded['order_tracking_number'],
                                    track_uri_decoded['line_item_id'],
                                    self._download_server_address,
                                    self._download_url_footer,
                                    track_uri_decoded['track_file_name'],
                                    self._credentials,
                                    self._session)

    def _get_chapters(self, line_item_id, order_tracking_number):
        return api.get_chapters(order_tracking_number, line_item_id, self._credentials, self._session)


def track_uri_decode(track_uri):
    track_values = track_uri.split(':')
    return {
        'line_item_id': track_values[2],
        'order_tracking_number': track_values[3],
        'track_no': track_values[4],
        'track_file_name': track_values[5]
    }


def track_uri_encode(line_item_id, tracking_number, track_no, track_file_name):
    return 'audioteka:track:{0}:{1}:{2}:{3}'.format(line_item_id, tracking_number, track_no, track_file_name)


def album_uri_encode(line_item_id, tracking_number):
    return 'audioteka:album:{0}:{1}'.format(line_item_id, tracking_number)