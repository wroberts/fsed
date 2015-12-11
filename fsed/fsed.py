#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import fsed.ahocorasick

@cli.command()
@click.argument('batch_filename', type=click.Path(exists=True))
@click.argument('input_filename', default='-')
@click.argument('output_filename', default='-')
def make_input_acsr(batch_filename, input_filename, output_filename):
    # load the batch
    logger.info('make_input_acsr {} {} {}'.format(batch_filename, input_filename,
                                                  output_filename))
    candidates = []
    with utils.open_file(batch_filename) as batch_file:
        for line in batch_file:
            line = line.decode('utf-8').strip()
            candidates.append(line)
    logger.info('{} MWE candidates loaded'.format(len(candidates)))
    trie = ahocorasick.AhoCorasickTrie()
    for cand in candidates:
        trie[cand] = cand.replace(' ', '_')
    # search and replace on the
    with utils.open_file(input_filename) as input_file:
        with utils.open_file(output_filename, 'w') as output_file:
            logger.info('writing {} to {}'.format(input_filename,
                                                  output_filename))
            num_lines = 0
            for line in input_file:
                line = line.decode('utf-8').strip()
                line = trie.greedy_replace_w_sep(line)
                output_file.write((line + '\n').encode('utf-8'))
                num_lines += 1
            logger.info('{} lines written'.format(num_lines))
