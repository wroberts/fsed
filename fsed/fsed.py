#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals
import click
import fsed.ahocorasick
import logging
import sys

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    stream=sys.stderr, level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def set_log_level(verbose, quiet):
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

def build_trie(pattern_filename, pattern_format, on_word_boundaries):
    candidates = []
    with utils.open_file(batch_filename) as batch_file:
        for line in batch_file:
            line = line.decode('utf-8').strip()
            candidates.append(line)
    LOGGER.info('{} patterns loaded'.format(len(candidates)))
    trie = fsed.ahocorasick.AhoCorasickTrie()
    for cand in candidates:
        trie[cand] = cand.replace(' ', '_')
    return trie

@click.command()
@click.argument('pattern_filename', type=click.Path(exists=True),
                metavar='PATTERN_FILE')
@click.argument('input_filenames', default='-', nargs=-1,
                metavar='[INPUT_FILES]')
@click.option('--pattern-format', type=click.Choice(['tsv', 'sed']),
              default='sed', show_default=True,
              help='Specify the format of PATTERN_FILE')
@click.option('-o', '--output', 'output_filename', type=click.Path(),
              help='Program output is written '
              'to this file. Default is to write '
              'to standard output.')
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
         words, by_line, slow, verbose, quiet):
    '''
    Search and replace on INPUT_FILE(s) (or standard input), with
    matching on fixed strings.
    '''
    set_log_level(verbose, quiet)
    if slow:
        by_line = True
    # load the batch
    LOGGER.info('fsed {} input {} output {}'.format(pattern_filename,
                                                    input_filenames,
                                                    output_filename))
    # build trie machine for matching
    trie = build_trie(pattern_filename, pattern_format, words)
    # search and replace on the
    with utils.open_file(input_filename) as input_file:
        with utils.open_file(output_filename, 'w') as output_file:
            LOGGER.info('writing {} to {}'.format(input_filename,
                                                  output_filename))
            num_lines = 0
            for line in input_file:
                line = line.decode('utf-8').strip()
                line = trie.greedy_replace_w_sep(line)
                output_file.write((line + '\n').encode('utf-8'))
                num_lines += 1
            LOGGER.info('{} lines written'.format(num_lines))

if __name__ == '__main__':
    main()
