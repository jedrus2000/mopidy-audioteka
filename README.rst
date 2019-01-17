****************************
Mopidy-Audioteka
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-Audioteka.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Audioteka/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/jedrus2000/mopidy-audioteka/master.svg?style=flat
    :target: https://travis-ci.org/jedrus2000/mopidy-audioteka
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/jedrus2000/mopidy-audioteka/master.svg?style=flat
   :target: https://coveralls.io/r/jedrus2000/mopidy-audioteka
   :alt: Test coverage


`Mopidy <https://www.mopidy.com/>`_ extension (non-official) for `Audioteka <https://audioteka.com/>`_ audiobooks service.


Installation
============

Install by running::

    pip install Mopidy-Audioteka

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-Audioteka to your Mopidy configuration file::

    [audioteka]
    enabled = true
    username = account name at Audioteka
    password = password for above account name


Project resources
=================

- `Source code <https://github.com/jedrus2000/mopidy-audioteka>`_
- `Issue tracker <https://github.com/jedrus2000/mopidy-audioteka/issues>`_


Credits
=======

- Original author: `Andrzej Bargański <https://github.com/jedrus2000>`_
- Current maintainer: `Andrzej Bargański <https://github.com/jedrus2000>`_
- `Contributors <https://github.com/jedrus2000/mopidy-audioteka/graphs/contributors>`_


Changelog
=========

v0.1.2 (2019-01-17)
----------------------------------------

- Initial release.
