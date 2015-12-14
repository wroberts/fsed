#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
utils.py
(c) Will Roberts  12 December, 2015

Utility functions.
'''

from __future__ import absolute_import
from fsed.compat import PY3, string_type
import sys

def open_file(filename, mode='r'):
    """
    Opens a file for access with the given mode.  This function
    transparently wraps gzip and xz files as well as normal files.
    You can also open zip files using syntax like:

    f = utils.open_file('../semcor-parsed.zip:semcor000.txt')
    """
    if (('r' not in mode or hasattr(filename, 'read')) and
        (('a' not in mode and 'w' not in mode) or hasattr(filename, 'write')) and
        hasattr(filename, '__iter__')):
        return filename
    elif isinstance(filename, string_type):
        if filename == '-' and 'r' in mode:
            if PY3:
                return sys.stdin.buffer
        elif filename == '-' and ('w' in mode or 'a' in mode):
            if PY3:
                return sys.stdout.buffer
        if filename.lower().count('.zip:'):
            assert 'r' in mode
            assert filename.count(':') == 1
            import zipfile
            zipped_file = zipfile.ZipFile(filename.split(':')[0])
            unzipped_file = zipped_file.open(filename.split(':')[1], 'r')
            zipped_file.close()
            return unzipped_file
        elif filename.lower().endswith('.gz'):
            import gzip
            return gzip.open(filename, mode)
        elif filename.lower().endswith('.xz'):
            import lzma
            tmp = lzma.LZMAFile(filename, mode)
            dir(tmp)
            return tmp
        else:
            return open(filename, mode)
    else:
        raise Exception('Unknown type for argument filename')
