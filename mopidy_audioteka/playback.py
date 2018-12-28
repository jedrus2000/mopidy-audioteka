from __future__ import unicode_literals

import logging

from mopidy import backend


logger = logging.getLogger(__name__)


# These GStreamer caps matches the audio data provided by libspotify
#GST_CAPS = 'audio/x-raw,format=S16LE,rate=44100,channels=2,layout=interleaved'

# Extra log level with lower importance than DEBUG=10 for noisy debug logging
TRACE_LOG_LEVEL = 5


class AudiotekaPlaybackProvider(backend.PlaybackProvider):

    def __init__(self, *args, **kwargs):
        super(AudiotekaPlaybackProvider, self).__init__(*args, **kwargs)

    def translate_uri(self, uri):
        track_id = uri.rsplit(':')[-1]

        # TODO
        #stream_uri = self.backend.session.get_stream_url(
        #    track_id, quality=quality)
        stream_uri = 'http://' + track_id

        logger.debug('Translated: %s -> %s', uri, stream_uri)
        return stream_uri