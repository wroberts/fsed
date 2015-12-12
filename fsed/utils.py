#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
utils.py
(c) Will Roberts  12 December, 2015

Utility functions.
'''

import sys

def open_file(filename, mode='r'):
    """
    Opens a file for access with the given mode.  This function
    transparently wraps gzip and xz files as well as normal files.
    You can also open zip files using syntax like:

    f = utils.open_file('../semcor-parsed.zip:semcor000.txt')
    """
    if (hasattr(filename, 'read') and
        hasattr(filename, 'write') and
        hasattr(filename, '__iter__')):
        return filename
    elif isinstance(filename, basestring):
        if filename == '-' and 'r' in mode:
            return sys.stdin
        elif filename == '-' and ('w' in mode or 'a' in mode):
            return sys.stdout
        if filename.lower().count('.zip:'):
            assert mode == 'r'
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
