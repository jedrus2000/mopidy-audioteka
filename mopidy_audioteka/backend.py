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
        self.audioteka = audioteka.Audioteka(config['audioteka']['username'], config['audioteka']['password'])

        #self._actor_proxy = None
        #self._session = None
        #self._event_loop = None
        #self._bitrate = None
        #self._web_client = None

        self.library = library.AudiotekaLibraryProvider(backend=self)
        self.playback = playback.AudiotekaPlaybackProvider(
            audio=audio, backend=self)
        #if config['spotify']['allow_playlists']:
        #    self.playlists = playlists.SpotifyPlaylistsProvider(backend=self)
        #else:
        self.playlists = None
        self.uri_schemes = ['audioteka']
