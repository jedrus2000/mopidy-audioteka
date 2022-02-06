import logging
import pykka

from mopidy import backend


from mopidy_audioteka import library, playback, audioteka


logger = logging.getLogger(__name__)


class AudiotekaBackend(pykka.ThreadingActor, backend.Backend):
    uri_schemes = ['audioteka']

    def __init__(self, config, audio):
        super(AudiotekaBackend, self).__init__()

        self.config = config
        self.audio = audio

        self.audioteka = audioteka.Audioteka(
            config['proxy'], config['audioteka']['username'],
            config['audioteka']['password'],
            config['audioteka']['device_id']
        )
        self.library = library.AudiotekaLibraryProvider(backend=self)
        self.playback = playback.AudiotekaPlaybackProvider(
            audio=audio, backend=self, cache_dir=config['core']['cache_dir'])
        self.playlists = None

    def on_start(self):
        logger.info('Start refreshing Audioteka')
        self.library.refresh()
