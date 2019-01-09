# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import pykka

from mopidy import backend, httpclient


from mopidy_audioteka import Extension, library, playback, audioteka


logger = logging.getLogger(__name__)


class AudiotekaBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(AudiotekaBackend, self).__init__()

        self.config = config
        self.audio = audio
        self.audioteka = audioteka.Audioteka(backend=self)

        self.library = library.AudiotekaLibraryProvider(backend=self)
        self.playback = playback.AudiotekaPlaybackProvider(
            audio=audio, backend=self, config=config)

        self.playlists = None
        self.uri_schemes = ['audioteka']

    def on_start(self):
        logger.info('Start refreshing Audioteka')
        self.library.refresh()
