#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
compat.py
(c) Will Roberts  14 December, 2015

Python 2/3 compatibility layer, based on six.

Cribbed from:

https://github.com/nltk/nltk/raw/develop/nltk/compat.py
'''

from __future__ import absolute_import, print_function
import sys

PY3 = sys.version_info[0] == 3

if PY3:
    string_type = str
    binary_type = bytes
else:
    string_type = basestring
    binary_type = str
