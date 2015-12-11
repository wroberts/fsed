================================================
 fsed - Aho-Corasick string replacement utility
================================================

Search and replace on file(s), with matching on fixed strings.

Usage::

    fsed [OPTIONS] PATTERN_FILE [INPUT_FILE [INPUT_FILE2 ...]]

If one or more ``INPUT_FILEs`` are specified, ``fsed`` reads and
concatenates these as its input; otherwise, ``fsed`` reads the
standard input.
    
Options:

``--pattern-format=FMT``
    set FMT to ``tsv`` or ``sed`` (default is ``sed``) to specify the
    format of ``PATTERN_FILE``.

``-o/--output=OUTFILE``
    specify that the program output should be written to ``OUTFILE``.
    If this option is not used, ``fsed`` writes to standard output.

``-v/--verbose``
    turn on debugging output.

Pattern File
============

``PATTERN_FILE`` contains a list of patterns to search and replace in
the input; each pattern is listed on a separate line.  ``fsed``
supports two formats for specifying patterns.  The default, ``sed``,
specifies strings and their replacements the way the ``sed`` utility
does::

    s/SEARCH/REPLACE/

The character following the ``s`` character is the delimiter, and can
be any character (it does not have to be a forward slash).

The other format, ``tsv``, specifies patterns using ``<TAB>``
characters as delimiters::

    SEARCH<TAB>REPLACE

In this format, there must be only one ``<TAB>`` character per line.
