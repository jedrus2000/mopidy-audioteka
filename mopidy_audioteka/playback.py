# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import threading
from pathlib2 import Path
import logging

from mopidy import backend
from mopidy_audioteka import audioteka

logger = logging.getLogger(__name__)


download_few_chunks_event = threading.Event()


class AudiotekaPlaybackProvider(backend.PlaybackProvider):

    def __init__(self, *args, **kwargs):
        self._cache_dir = kwargs.pop('cache_dir')
        super(AudiotekaPlaybackProvider, self).__init__(*args, **kwargs)

    def translate_uri(self, track_uri):
        track_uri_decoded = audioteka.track_uri_decode(track_uri)
        track = self.backend.library.tracks.get(track_uri)
        if not track:
            logger.error("Can't find Track for uri: %s" % track_uri)
            return None

        file_name_path = Path(self._cache_dir, track_uri_decoded['track_no'])
        _fake_file_size(file_name_path, track.file_size)
        r = self.backend.audioteka.download_track(track_uri_decoded, True)
        download_few_chunks_event.clear()

        t1 = FuncThread(_download_and_save_chunks, r, file_name_path)
        t1.start()

        logger.debug('Playback. Waiting for first data chunk...')
        download_few_chunks_event.wait(10.0)
        logger.debug('Playback. Wait has ended.')

        stream_uri = 'file://' + str(file_name_path)

        logger.debug('Playback. Translated: %s -> %s', track_uri, stream_uri)
        return stream_uri


class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


def _download_and_save_chunks(r, file_name):
    chunks = 0
    with open(str(file_name), 'r+b') as f:
        f.seek(0)
        for chunk in r.iter_content(chunk_size=2048):
            if chunk:
                f.write(chunk)
                chunks += len(chunk)
                if (chunks > 1000000) and (not download_few_chunks_event.is_set()):
                    logger.debug('Playback. Wait release. %s bytes of chunks downloaded.' % chunks)
                    download_few_chunks_event.set()
        logger.debug("Playback. Finished downloading %s" % file_name)
        download_few_chunks_event.set()


def _fake_file_size(file_name, file_size):
    with open(str(file_name), "wb") as f:
        f.seek(file_size-1)
        f.write(b"\0")
