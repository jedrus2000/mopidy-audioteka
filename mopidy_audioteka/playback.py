from __future__ import unicode_literals

from pathlib2 import Path
import logging

from mopidy import backend
from mopidy_audioteka import audioteka

logger = logging.getLogger(__name__)


# These GStreamer caps matches the audio data provided by libspotify
#GST_CAPS = 'audio/x-raw,format=S16LE,rate=44100,channels=2,layout=interleaved'

# Extra log level with lower importance than DEBUG=10 for noisy debug logging
TRACE_LOG_LEVEL = 5


class AudiotekaPlaybackProvider(backend.PlaybackProvider):

    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop('config')
        super(AudiotekaPlaybackProvider, self).__init__(*args, **kwargs)

    def translate_uri(self, track_uri):
        track_uri_decoded = audioteka.track_uri_decode(track_uri)
        r = self.backend.audioteka.download_track(track_uri_decoded)
        file_name_path = Path(self.config['core']['cache_dir'], track_uri_decoded['track_no'])
        open(str(file_name_path), 'wb').write(r.content)

        stream_uri = 'file:' + str(file_name_path)

        logger.debug('Translated: %s -> %s', track_uri, stream_uri)
        return stream_uri
