================================================
 fsed - Aho-Corasick string replacement utility
================================================

.. image:: https://travis-ci.org/wroberts/fsed.svg?branch=master
    :target: https://travis-ci.org/wroberts/fsed
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/wroberts/fsed/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/wroberts/fsed?branch=master
    :alt: Test code coverage

.. image:: https://img.shields.io/pypi/v/fsed.svg
    :target: https://pypi.python.org/pypi/fsed/
    :alt: Latest Version

Copyright (c) 2015 Will Roberts <wildwilhelm@gmail.com>

Licensed under the MIT License (see file ``LICENSE.rst`` for
details).

Search and replace on file(s), with matching on fixed strings.

``fsed`` is a tool specially designed for situations where you have to
do *many* string search-and-replace operations with fixed strings
(that is, ``fsed`` doesn't do regular expressions).  By doing all the
searching and replacing on all the patterns at the same time, ``fsed``
can be much faster than tools that do string rewriting one pattern at
a time (like one-liners in ``sed`` or ``perl``).

To do its searching, ``fsed`` uses the `Aho-Corasick algorithm`_,
which is a very clever way of matching multiple patterns at the same
time, and was used to implement the original `fgrep`_ Unix utility
(now accessed as ``grep -F``).  This algorithm is capable of finding
matches which overlap each other, and in these cases, ``fsed`` must
choose which matches to rewrite.  The policy adopted by ``fsed`` is to
be greedy, and always rewrite the shortest, leftmost match first.

For illustration, imagine a situation where we would like to rewrite
``a`` with ``b``, ``aa`` with ``c``, and ``aaa`` with ``d``.  What
should we do when we see the input string ``aaa``?  Should we produce
``bbb``, ``bc``, ``cb``, or ``d``?  ``fsed`` produces ``bbb`` in this
case.

.. _`Aho-Corasick algorithm`: https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm
.. _fgrep: https://en.wikipedia.org/wiki/Grep#Variations

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

Note: ``fsed`` runs even faster using PyPy_::

    pypy -m fsed.fsed [OPTIONS] PATTERN_FILE [INPUT_FILE [INPUT_FILE2 ...]]

.. _PyPy: http://pypy.org/

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
