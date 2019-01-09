# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='Mopidy-Audioteka',
    version=get_version('mopidy_audioteka/__init__.py'),
    url='https://github.com/jedrus2000/mopidy-audioteka',
    license='Apache License, Version 2.0',
    author=u'Andrzej Bargański',
    author_email='a.barganski@gmail.com',
    description='Mopidy extension for Audioteka',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 1.0',
        'Pykka >= 1.1',
        'audtekapi >= 0.1.0',
    ],
    entry_points={
        'mopidy.ext': [
            'audioteka = mopidy_audioteka:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
