#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
ahocorasick.py
(c) Will Roberts  18 June, 2015

Second attempt writing Aho-Corasick string matching in Python.
'''

from __future__ import absolute_import, print_function, unicode_literals
from collections import deque
import sys
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    stream=sys.stderr, level=logging.INFO)
LOGGER = logging.getLogger(__name__)


# ============================================================
#  NODE IN A TRIE
# ============================================================

class TrieNode(dict):
    '''A node in a Trie.'''

    def __init__(self):
        '''Constructor.'''
        super(TrieNode, self).__init__()
        self._value = None
        self.has_value = False
        self.depth = 0
        self.prefix = ''
        self.uplink = None
        # suffix is a tuple of (TrieNode, length)
        self.suffix = None
        # likewise, dict_suffix is a tuple of (TrieNode, length)
        self.dict_suffix = None

    def __unicode__(self):
        if self.depth == 0:
            return '<ROOT>'
        rv = self.prefix
        if self.has_value:
            rv += ' (value = "{}")'.format(self._value)
        if self.has_suffix:
            rv += ' (suffix = "{}")'.format(self.suffix.prefix)
        if self.has_dict_suffix:
            rv += ' (dict_suffix = "{}")'.format(self.dict_suffix.prefix)
        return rv

    def __repr__(self):
        return '<TrieNode prefix "{}" keys {}>'.format(self.prefix, self.keys())

    @property
    def value(self):
        '''Gets this node's value.'''
        return self._value

    @value.setter
    def value(self, v):
        '''Sets this node's value.'''
        self._value = v
        self.has_value = True

    @property
    def has_suffix(self):
        return self.suffix is not None

    @property
    def has_dict_suffix(self):
        return self.dict_suffix is not None


# ============================================================
#  BASE TRIE
# ============================================================

class Trie(object):
    '''A Trie which stores values.'''

    def __init__(self):
        '''Constructor.'''
        self.root = TrieNode()

    def __contains__(self, seq):
        current = self.root
        for char in seq:
            if char not in current:
                return False
            current = current[char]
        if not current.has_value:
            return False
        return True

    def __getitem__(self, seq):
        current = self.root
        for char in seq:
            if char not in current:
                raise KeyError(seq)
            current = current[char]
        if not current.has_value:
            raise KeyError(seq)
        return current.value

    def __setitem__(self, seq, value):
        current = self.root
        for char in seq:
            if char not in current:
                new_node = TrieNode()
                new_node.uplink = char
                new_node.depth = current.depth + 1
                new_node.prefix = current.prefix + char
                current[char] = new_node
            current = current[char]
        current.value = value

    def pretty_print(self):
        # dfs
        todo = [self.root]
        while todo:
            current = todo.pop()
            for char in reversed(sorted(current.keys())):
                todo.append(current[char])
            indent = ' ' * (current.depth * 2)
            print(indent + unicode(current))


# ============================================================
#  AHO-CORASICK TRIE
# ============================================================

class AhoCorasickTrie(Trie):
    '''A Trie object for performing Aho-Corasick string matching.'''

    def __init__(self):
        '''Constructor.'''
        super(AhoCorasickTrie, self).__init__()
        self._suffix_links_set = False

    def __setitem__(self, seq, value):
        super(AhoCorasickTrie, self).__setitem__(seq, value)
        if self._suffix_links_set:
            self._reset_suffix_links()

    def _reset_suffix_links(self):
        self._suffix_links_set = False
        # dfs
        todo = [self.root]
        while todo:
            current = todo.pop()
            for char in current:
                todo.append(current[char])
            current.suffix = None
            current.dict_suffix = None

    def _set_suffix_links(self):
        self._suffix_links_set = True
        # bfs
        todo = deque([(self.root[char], self.root) for char in self.root])
        while todo:
            current, parent = todo.popleft()
            for char in current:
                todo.append((current[char], current))
            # the root doesn't get a suffix link
            # also, skip previously set suffix links
            if current.has_suffix:
                continue
            # current is not the root and has no suffix
            # set current's suffix to parent's suffix
            suffix = parent
            while True:
                if not suffix.has_suffix:
                    current.suffix = self.root
                    break
                else:
                    suffix = suffix.suffix
                if current.uplink in suffix:
                    current.suffix = suffix[current.uplink]
                    break
            # now find the dict_suffix value
            suffix = current.suffix
            while not suffix.has_value and suffix.has_suffix:
                suffix = suffix.suffix
            if suffix.has_value:
                current.dict_suffix = suffix

    def find_all(self, seq):
        '''
        Generator expression.  Yields tuples of `(begin, length, value)`,
        where:

        - `begin` is an integer identifying the character index where
          the match begins (0-based)
        - `length` is an integer indicating the length of the match (1
          or more characters)
        - `value` is the value of the matching node in the trie
        '''
        if not self._suffix_links_set:
            self._set_suffix_links()
        current = self.root
        for pos, char in enumerate(seq):
            # find a state where we can transition on char
            while char not in current and current.has_suffix:
                current = current.suffix
            if char in current:
                # transition
                current = current[char]
            else:
                # we must be at the root node
                assert current is self.root
                # throw out the char without doing anything
                pass
            # now perform any matching on the current node
            if current.has_value:
                yield (1 + pos - current.depth, current.depth, current.value)
            dict_suffix = current
            while dict_suffix.has_dict_suffix:
                dict_suffix = dict_suffix.dict_suffix
                yield (1 + pos - dict_suffix.depth, dict_suffix.depth, dict_suffix.value)

    def greedy_replace_w_sep(self, seq):
        if not self._suffix_links_set:
            self._set_suffix_links()
        current = self.root
        rv = ''
        buffered = ''
        seq_len_l1 = len(seq) - 1
        for pos, char in enumerate(seq):
            while not char in current and current.has_suffix:
                current = current.suffix
            if char in current:
                current = current[char]
                buffered += char
            else:
                rv += buffered + char
                buffered = ''
            reduced = False
            if current.has_value:
                # scan back to find the char before current started
                depth, value = current.depth, current.value
                begin_pos = pos - depth
                begin_boundary = begin_pos < 0 or seq[begin_pos] == ' '
                end_boundary = pos == seq_len_l1 or seq[pos+1] == ' '
                if begin_boundary and end_boundary:
                    rv += buffered[:-depth] + value
                    buffered = ''
                    current = self.root
                    reduced = True
            if not reduced and current.has_dict_suffix:
                # scan back to find the char before current started
                depth, value = current.dict_suffix.depth, current.dict_suffix.value
                begin_pos = pos - depth
                begin_boundary = begin_pos < 0 or seq[begin_pos] == ' '
                end_boundary = pos == seq_len_l1 or seq[pos+1] == ' '
                if begin_boundary and end_boundary:
                    rv += buffered[:-depth] + value
                    buffered = ''
                    current = self.root
                    reduced = True
        reduced = False
        if current.has_value:
            # scan back to find the char before current started
            depth, value = current.depth, current.value
            begin_pos = pos - depth
            begin_boundary = begin_pos < 0 or seq[begin_pos] == ' '
            end_boundary = pos == seq_len_l1 or seq[pos+1] == ' '
            if begin_boundary and end_boundary:
                rv += buffered[:-depth] + value
                reduced = True
        if not reduced and current.has_dict_suffix:
            # scan back to find the char before current started
            depth, value = current.dict_suffix.depth, current.dict_suffix.value
            begin_pos = pos - depth
            begin_boundary = begin_pos < 0 or seq[begin_pos] == ' '
            end_boundary = pos == seq_len_l1 or seq[pos+1] == ' '
            if begin_boundary and end_boundary:
                rv += buffered[:-depth] + value
                reduced = True
        if not reduced:
            rv += buffered
        return rv

    def replace(self, seq):
        '''
        Performs search and replace on the given input string `seq` using
        the values stored in this trie.  This method uses a O(n**2)
        chart-parsing algorithm to find the optimal way of replacing
        matches in the input.

        Arguments:
        - `seq`:
        '''
        # chart is a (n-1) X (n) table
        # chart[0] represents all matches of length (0+1) = 1
        # chart[n-1] represents all matches/rewrites of length (n-1+1) = n
        # chart[0][0] represents a match of length 1 starting at character 0
        # chart[0][n-1] represents a match of length 1 starting at character n-1
        # cells in the chart are tuples:
        #    (score, list)
        # we initialise chart by filling in row 0:
        #    each cell gets assigned (0, char), where char is the character at
        #    the corresponding position in the input string
        chart = [ [None for i in range(len(seq)) ] for i in range(len(seq)) ]
        chart[0] = [(0, char) for char in seq]
        # now we fill in the chart using the results from the aho-corasick
        # string matches
        for (begin, length, value) in self.find_all(seq):
            chart[length-1][begin] = (length, value)
        # now we need to fill in the chart row by row, starting with row 1
        for row in range(1, len(chart)):
            # each row is 1 cell shorter than the last
            for col in range(len(seq) - row):
                # the entry in [row][col] is the choice with the highest score; to
                # find this, we must search the possible partitions of the cell
                #
                # things on row 2 have only one possible partition: 1 + 1
                # things on row 3 have two: 1 + 2, 2 + 1
                # things on row 4 have three: 1+3, 3+1, 2+2
                #
                # we assume that any pre-existing entry found by aho-corasick
                # in a cell is already optimal
                #print('scanning [{}][{}]'.format(row, col))
                if chart[row][col] is not None:
                    continue
                # chart[1][2] is the cell of matches of length 2 starting at
                # character position 2;
                # it can only be composed of chart[0][2] + chart[0][3]
                #
                # partition_point is the length of the first of the two parts
                # of the cell
                #print('cell[{}][{}] => '.format(row, col))
                best_score = -1
                best_value = None
                for partition_point in range(row):
                    # the two cells will be [partition_point][col] and
                    # [row - partition_point - 2][col+partition_point+1]
                    x1 = partition_point
                    y1 = col
                    x2 = row - partition_point - 1
                    y2 = col + partition_point + 1
                    #print('   [{}][{}] + [{}][{}]'.format(x1, y1, x2, y2))
                    s1, v1 = chart[x1][y1]
                    s2, v2 = chart[x2][y2]
                    # compute the score
                    score = s1 + s2
                    #print('   = {}  +  {}'.format((s1, v1), (s2, v2)))
                    #print('   = score {}'.format(score))
                    if best_score < score:
                        best_score = score
                        best_value = v1 + v2
                        chart[row][col] = (best_score, best_value)
                        #print('   sets new best score with value {}'.format(
                        #    best_value))
        # now the optimal solution is stored at the top of the chart
        return chart[len(seq)-1][0][1]

    def greedy_replace(self, seq):
        if not self._suffix_links_set:
            self._set_suffix_links()
        # start at the root
        current = self.root
        buffered = ''
        outstr = ''
        for char in seq:
            while char not in current:
                if current.has_dict_suffix:
                    current = current.dict_suffix
                    outstr += buffered[:-current.depth]
                    outstr += current.value
                    buffered = ''
                    current = self.root
                    break
                elif current.has_suffix:
                    current = current.suffix
                    if current.depth:
                        outstr += buffered[:-current.depth]
                        buffered = buffered[-current.depth:]
                    else:
                        outstr += buffered
                        buffered = ''
                        break
                else:
                    current = self.root
                    outstr += buffered
                    buffered = ''
                    break
            if char in current:
                buffered += char
                current = current[char]
                if current.has_value:
                    outstr += buffered[:-current.depth]
                    outstr += current.value
                    buffered = ''
                    current = self.root
            else:
                assert current is self.root
                outstr += buffered + char
                buffered = ''
        if current.has_dict_suffix:
            current = current.dict_suffix
            outstr += buffered[:-current.depth]
            outstr += current.value
        else:
            outstr += buffered
        return outstr

WHITESPACE_CHARS = ' \t\v\r\n'

def boundary_transform(seq, force_edges = True):
    gen = boundary_words(seq)
    if force_edges:
        gen = boundary_edges(gen)
    gen = remove_duplicates(gen)
    for char in gen:
        yield char

def boundary_words(seq):
    in_word = None
    for char in seq:
        if char == '\x00' and in_word is not None:
            in_word = not in_word
        elif char in WHITESPACE_CHARS:
            if in_word is not None and in_word:
                yield '\x00'
            in_word = False
        else:
            if in_word is not None and not in_word:
                yield '\x00'
            in_word = True
        yield char

def boundary_edges(seq):
    yield '\x00'
    for char in seq:
        yield char
    yield '\x00'

def remove_duplicates(seq):
    last_boundary = False
    for char in seq:
        if char == '\x00':
            if not last_boundary:
                last_boundary = True
                yield char
        else:
            last_boundary = False
            yield char

def boundary_untransform(seq):
    for char in seq:
        if char != '\x00':
            yield char
