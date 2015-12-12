================================================
 fsed - Aho-Corasick string replacement utility
================================================

.. image:: https://travis-ci.org/wroberts/fsed.svg?branch=master
    :target: https://travis-ci.org/wroberts/fsed
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/wroberts/fsed/badge.svg
    :target: https://coveralls.io/r/wroberts/fsed
    :alt: Test code coverage

.. image:: https://img.shields.io/pypi/v/fsed.svg
    :target: https://pypi.python.org/pypi/fsed/
    :alt: Latest Version

Copyright (c) 2015 Will Roberts <wildwilhelm@gmail.com>

Licensed under the MIT License (see file ``LICENSE.rst`` for
details).

Search and replace on file(s), with matching on fixed strings.

Install
=======

``fsed`` is written in Python_; you can install it with pip_::

    pip install fsed

.. _Python: http://www.python.org/
.. _pip: https://en.wikipedia.org/wiki/Pip_(package_manager)

Usage
=====

::

    fsed [OPTIONS] PATTERN_FILE [INPUT_FILE [INPUT_FILE2 ...]]

If one or more ``INPUT_FILEs`` are specified, ``fsed`` reads and
concatenates these as its input; otherwise, ``fsed`` reads the
standard input.

Options:

``--pattern-format=FMT``
    Set FMT to ``tsv`` or ``sed`` (default is ``sed``) to specify the
    format of ``PATTERN_FILE``.

``-o/--output=OUTFILE``
    Specifies that the program output should be written to ``OUTFILE``.
    If this option is not used, ``fsed`` writes to standard output.

``-w/--words``
    Makes ``fsed`` match only on word boundaries; this flag instructs
    ``fsed`` to append ``\b`` to the beginning and end of every
    pattern in ``PATTERN_FILE``.

``--by-line/--across-lines``
    Sets whether ``fsed`` should process the input line by line
    or character by character; the default is ``--across-lines``.

``--slow``
    Indicates that ``fsed`` should try very hard to always find the
    longest matches on the input; this is very slow, and forces
    ``--by-line`` to be on.

``-q``
    Quiet operation, do not emit warnings.

``-v/--verbose``
    Turns on debugging output.

Pattern File
============

``PATTERN_FILE`` contains a list of patterns to search and replace in
the input; each pattern is listed on a separate line.  ``fsed``
supports two formats for specifying patterns.  The default, ``sed``,
specifies strings and their replacements the way the ``sed`` utility
does::

    s/SEARCH/REPLACE/

The character following the ``s`` character is the pattern delimiter,
and can be any character (it does not have to be a forward slash).

The other format, ``tsv``, specifies patterns using ``<TAB>``
characters as delimiters::

    SEARCH<TAB>REPLACE

In this format, there must be only one ``<TAB>`` character per line.

Patterns can contain escape characters:

``\\``
    Backslash (\\)

``\a``
    ASCII bell (BEL)

``\b``
    Word boundary

``\f``
    ASCII formfeed (FF)

``\n``
    ASCII linefeed (LF)

``\r``
    Carriage Return (CR)

``\t``
    Horizontal Tab (TAB)

``\v``
    ASCII vertical tab (VT)
