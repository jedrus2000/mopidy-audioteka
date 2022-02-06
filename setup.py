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
    description='Mopidy backend extension for Audioteka',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 3.0',
        'Pykka >= 2.0.1',
        'audtekapi >= 0.3.0',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
