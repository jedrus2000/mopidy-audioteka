import logging

from mopidy import backend
from mopidy_audioteka import audioteka

logger = logging.getLogger(__name__)


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

        stream_uri = self.backend.audioteka.get_stream_url(track_uri_decoded)

        logger.debug('Playback. Translated: %s -> %s', track_uri, stream_uri)
        return stream_uri

