#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals
from fsed.utils import open_file
import click
import fsed.ahocorasick
import logging
import re
import sys

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    stream=sys.stderr, level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def set_log_level(verbose, quiet):
    '''
    Ses the logging level of the script based on command line options.

    Arguments:
    - `verbose`:
    - `quiet`:
    '''
    '''Sets the logging level.'''
    if quiet:
        verbose = -1
    if verbose < 0:
        verbose = logging.CRITICAL
    elif verbose == 1:
        verbose = logging.INFO
    elif 1 < verbose:
        verbose = logging.DEBUG
    LOGGER.setLevel(verbose)
    fsed.ahocorasick.LOGGER.setLevel(verbose)

def detect_pattern_format(pattern_filename, encoding, on_word_boundaries):
    '''
    Automatically detects the pattern file format, and determines
    whether the Aho-Corasick string matching should pay attention to
    word boundaries or not.

    Arguments:
    - `pattern_filename`:
    - `encoding`:
    - `on_word_boundaries`:
    '''
    tsv = True
    boundaries = on_word_boundaries
    with open_file(pattern_filename) as input_file:
        for line in input_file:
            line = line.decode(encoding)
            if line.count('\t') != 1:
                tsv = False
            if '\\b' in line:
                boundaries = True
            if boundaries and not tsv:
                break
    return tsv, boundaries

def sub_escapes(sval):
    '''
    Process escaped characters in ``sval``.

    Arguments:
    - `sval`:
    '''
    sval = sval.replace('\\a', '\a')
    sval = sval.replace('\\b', '\x00')
    sval = sval.replace('\\f', '\f')
    sval = sval.replace('\\n', '\n')
    sval = sval.replace('\\r', '\r')
    sval = sval.replace('\\t', '\t')
    sval = sval.replace('\\v', '\v')
    sval = sval.replace('\\\\', '\\')
    return sval

def build_trie(pattern_filename, pattern_format, encoding, on_word_boundaries):
    '''
    Constructs a finite state machine for performing string rewriting.

    Arguments:
    - `pattern_filename`:
    - `pattern_format`:
    - `encoding`:
    - `on_word_boundaries`:
    '''
    boundaries = on_word_boundaries
    if pattern_format == 'auto' or not on_word_boundaries:
        tsv, boundaries = detect_pattern_format(pattern_filename, encoding,
                                                on_word_boundaries)
    if pattern_format == 'auto':
        if tsv:
            pattern_format = 'tsv'
        else:
            pattern_format = 'sed'
    trie = fsed.ahocorasick.AhoCorasickTrie()
    num_candidates = 0
    with open_file(pattern_filename) as pattern_file:
        for lineno, line in enumerate(pattern_file):
            line = line.decode(encoding).rstrip('\n')
            if not line.strip():
                continue
            # decode the line
            if pattern_format == 'tsv':
                fields = line.split('\t')
                if len(fields) != 2:
                    LOGGER.warning(('skipping line {} of pattern file (not '
                                    'in tab-separated format): {}').format(lineno, line))
                    continue
                before, after = fields
            elif pattern_format == 'sed':
                before = after = None
                line = line.lstrip()
                if line[0] == 's':
                    delim = line[1]
                    fields = re.split(r'(?<!\\){}'.format(delim), line)
                    if len(fields) == 4:
                        before, after = fields[1], fields[2]
                        before = re.sub(r'(?<!\\)\\{}'.format(delim), delim, before)
                        after = re.sub(r'(?<!\\)\\{}'.format(delim), delim, after)
                if before is None or after is None:
                    LOGGER.warning(('skipping line {} of pattern file (not '
                                    'in sed format): {}').format(lineno, line))
                    continue
            num_candidates += 1
            if on_word_boundaries and before != before.strip():
                LOGGER.warning(('before pattern on line {} padded whitespace; '
                                'this may interact strangely with the --words '
                                'option: {}').format(lineno, line))
            before = sub_escapes(before)
            after = sub_escapes(after)
            if boundaries:
                before = fsed.ahocorasick.boundary_transform(before, on_word_boundaries)
            trie[before] = after
    LOGGER.info('{} patterns loaded from {}'.format(num_candidates,
                                                    pattern_filename))
    return trie, boundaries

def rewrite_str_with_trie(sval, trie, boundaries = False, slow = False):
    '''
    Rewrites a string using the given trie object.

    Arguments:
    - `sval`:
    - `trie`:
    - `boundaries`:
    - `slow`:
    '''
    if boundaries:
        sval = fsed.ahocorasick.boundary_transform(sval)
    if slow:
        sval = trie.replace(sval)
    else:
        sval = trie.greedy_replace(sval)
    if boundaries:
        sval = ''.join(fsed.ahocorasick.boundary_untransform(sval))
    return sval

@click.command()
@click.argument('pattern_filename', type=click.Path(exists=True),
                metavar='PATTERN_FILE')
@click.argument('input_filenames', default='-', nargs=-1,
                type=click.Path(exists=True), metavar='[INPUT_FILES]')
@click.option('--pattern-format', type=click.Choice(['auto', 'tsv', 'sed']),
              default='auto', show_default=True,
              help='Specify the format of PATTERN_FILE')
@click.option('-o', '--output', 'output_filename', type=click.Path(),
              help='Program output is written '
              'to this file. Default is to write '
              'to standard output.')
@click.option('-e', '--encoding', default='utf-8', show_default=True,
              help='The character encoding to use')
@click.option('-w', '--words', is_flag=True,
              help='Match only on word boundaries: '
              'appends "\\b" to the beginning and '
              'end of every pattern in PATTERN_FILE.')
@click.option('--by-line/--across-lines', default=False,
              help='Process the input line by '
              'line or character by character; the default is --across-lines.')
@click.option('--slow', is_flag=True,
              help='Try very hard to '
              'find the longest matches on the input; this is very slow, '
              'and forces --by-line.')
@click.option('-v', '--verbose', default=0, count=True,
              help='Turns on debugging output.')
@click.option('-q', '--quiet', is_flag=True,
              help='Quiet operation, do not emit warnings.')
def main(pattern_filename, input_filenames, pattern_format,
         output_filename,
         encoding, words, by_line, slow, verbose, quiet):
    '''
    Search and replace on INPUT_FILE(s) (or standard input), with
    matching on fixed strings.
    '''
    set_log_level(verbose, quiet)
    if slow:
        by_line = True
    by_line = True # TODO: implement non-line-based rewriting
    # load the patterns
    LOGGER.info('fsed {} input {} output {}'.format(pattern_filename,
                                                    input_filenames,
                                                    output_filename))
    if not input_filenames:
        input_filenames = ('-',)
    if not output_filename:
        output_filename = '-'
    # build trie machine for matching
    trie, boundaries = build_trie(pattern_filename, pattern_format, encoding, words)
    LOGGER.info('writing to {}'.format(output_filename))
    with open_file(output_filename, 'w') as output_file:
        for input_filename in input_filenames:
            # search and replace
            with open_file(input_filename) as input_file:
                LOGGER.info('reading {}'.format(input_filename))
                if by_line:
                    num_lines = 0
                    for line in input_file:
                        line = line.decode(encoding).rstrip('\n')
                        line = rewrite_str_with_trie(line, trie, boundaries, slow)
                        output_file.write((line + '\n').encode(encoding))
                        num_lines += 1
                    LOGGER.info('{} lines written'.format(num_lines))
                else:
                    raise NotImplementedError

if __name__ == '__main__':
    main()
