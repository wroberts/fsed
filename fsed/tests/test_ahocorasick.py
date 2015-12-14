#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test_ahocorasick.py
(c) Will Roberts  12 December, 2015

Unit tests for the ``ahocorasick`` module.
'''

from __future__ import absolute_import, print_function, unicode_literals
from .. import ahocorasick
import unittest

class TestAhocorasick(unittest.TestCase):
    '''
    Unit tests for the `ahocorasick` module.
    '''

    def test_boundary_transform(self):
        '''
        Test the boundary_transform.
        '''
        self.assertEqual(''.join(ahocorasick.boundary_transform('abc')),
                         '\x00abc\x00')
        self.assertEqual(''.join(ahocorasick.boundary_transform('abc def')),
                         '\x00abc\x00 \x00def\x00')
        self.assertEqual(''.join(ahocorasick.boundary_transform('  abc def  ')),
                         '\x00  \x00abc\x00 \x00def\x00  \x00')

    def test_boundary_transform_2(self):
        '''
        Test the boundary_transform.
        '''
        self.assertEqual(''.join(ahocorasick.boundary_transform('abc def')),
                         '\x00abc\x00 \x00def\x00')
        self.assertEqual(''.join(ahocorasick.boundary_transform('\x00abc def')),
                         '\x00abc\x00 \x00def\x00')
        self.assertEqual(''.join(ahocorasick.boundary_transform('abc def\x00')),
                         '\x00abc\x00 \x00def\x00')
        self.assertEqual(''.join(ahocorasick.boundary_transform('\x00abc def\x00')),
                         '\x00abc\x00 \x00def\x00')
        self.assertEqual(''.join(ahocorasick.boundary_transform('abc def', False)),
                         'abc\x00 \x00def')
        self.assertEqual(''.join(ahocorasick.boundary_transform('\x00abc def', False)),
                         '\x00abc\x00 \x00def')
        self.assertEqual(''.join(ahocorasick.boundary_transform('abc def\x00', False)),
                         'abc\x00 \x00def\x00')
        self.assertEqual(''.join(ahocorasick.boundary_transform('\x00abc def\x00', False)),
                         '\x00abc\x00 \x00def\x00')

    def test_transform_roundtrip(self):
        '''
        Test boundary_transform round trip.
        '''
        test_strings = ['', 'abc', 'abc def', '  abc def', '  abc def  ', 'abc def  ',]
        for force_edges in [False, True]:
            for test_string in test_strings:
                self.assertEqual(test_string,
                                 ''.join(ahocorasick.boundary_untransform(
                                     ahocorasick.boundary_transform(test_string,
                                                                    force_edges))))

    def test_debug1(self):
        '''
        Test case from Wikipedia.

        https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm
        '''
        trie = ahocorasick.Trie()
        trie['a'] = '(a)'
        trie['ab'] = '(ab)'
        trie['bab'] = '(bab)'
        trie['bc'] = '(bc)'
        trie['bca'] = '(bca)'
        trie['c'] = '(c)'
        trie['caa'] = '(caa)'
        debug_1_ppstr = '''<ROOT>
  a (value = "(a)")
    ab (value = "(ab)")
  b
    ba
      bab (value = "(bab)")
    bc (value = "(bc)")
      bca (value = "(bca)")
  c (value = "(c)")
    ca
      caa (value = "(caa)")'''
        self.assertEqual(trie.pretty_print_str(), debug_1_ppstr)

    def test_debug2(self):
        '''Hand-written test case.'''
        trie = ahocorasick.AhoCorasickTrie()
        trie['damn'] = '(damn)'
        trie['dog'] = '(dog)'
        trie['cat'] = '(cat)'
        trie['cablex'] = '(cablex)'
        trie._set_suffix_links()
        debug_2_ppstr1 = '''<ROOT>
  c (suffix = "")
    ca (suffix = "")
      cab (suffix = "")
        cabl (suffix = "")
          cable (suffix = "")
            cablex (value = "(cablex)") (suffix = "")
      cat (value = "(cat)") (suffix = "")
  d (suffix = "")
    da (suffix = "")
      dam (suffix = "")
        damn (value = "(damn)") (suffix = "")
    do (suffix = "")
      dog (value = "(dog)") (suffix = "")'''
        self.assertEqual(trie.pretty_print_str(), debug_2_ppstr1)
        trie['ogre'] = '(ogre)'
        trie._set_suffix_links()
        debug_2_ppstr2 = '''<ROOT>
  c (suffix = "")
    ca (suffix = "")
      cab (suffix = "")
        cabl (suffix = "")
          cable (suffix = "")
            cablex (value = "(cablex)") (suffix = "")
      cat (value = "(cat)") (suffix = "")
  d (suffix = "")
    da (suffix = "")
      dam (suffix = "")
        damn (value = "(damn)") (suffix = "")
    do (suffix = "o")
      dog (value = "(dog)") (suffix = "og")
  o (suffix = "")
    og (suffix = "")
      ogr (suffix = "")
        ogre (value = "(ogre)") (suffix = "")'''
        self.assertEqual(trie.pretty_print_str(), debug_2_ppstr2)

    def test_debug3(self):
        '''
        Test case from Wikipedia.

        https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm
        '''
        trie = ahocorasick.AhoCorasickTrie()
        trie['a'] = '(a)'
        trie['ab'] = '(ab)'
        trie['bab'] = '(bab)'
        trie['bc'] = '(bc)'
        trie['bca'] = '(bca)'
        trie['c'] = '(c)'
        trie['caa'] = '(caa)'
        trie._set_suffix_links()
        debug_3_ppstr = '''<ROOT>
  a (value = "(a)") (suffix = "")
    ab (value = "(ab)") (suffix = "b")
  b (suffix = "")
    ba (suffix = "a") (dict_suffix = "a")
      bab (value = "(bab)") (suffix = "ab") (dict_suffix = "ab")
    bc (value = "(bc)") (suffix = "c") (dict_suffix = "c")
      bca (value = "(bca)") (suffix = "ca") (dict_suffix = "a")
  c (value = "(c)") (suffix = "")
    ca (suffix = "a") (dict_suffix = "a")
      caa (value = "(caa)") (suffix = "a") (dict_suffix = "a")'''
        self.assertEqual(trie.pretty_print_str(),
                         debug_3_ppstr)
        self.assertEqual(list(trie.find_all('abccab')),
                         [(0, 1, '(a)'), (0, 2, '(ab)'), (1, 2, '(bc)'),
                          (2, 1, '(c)'), (3, 1, '(c)'), (4, 1, '(a)'),
                          (4, 2, '(ab)')])
        self.assertEqual(trie.replace('abccab'),
                         '(a)(bc)(c)(ab)')
        self.assertEqual(trie.greedy_replace('abccab'),
                         '(a)(bc)(c)(a)b')

    def test_debug4(self):
        '''Hand-written test case.'''
        trie = ahocorasick.AhoCorasickTrie()
        trie['x'] = '(x)'
        trie['xabc'] = '(xabc)'
        trie['ab'] = '(ab)'
        trie._set_suffix_links()
        debug_4_ppstr = '''<ROOT>
  a (suffix = "")
    ab (value = "(ab)") (suffix = "")
  x (value = "(x)") (suffix = "")
    xa (suffix = "a")
      xab (suffix = "ab") (dict_suffix = "ab")
        xabc (value = "(xabc)") (suffix = "")'''
        self.assertEqual(trie.pretty_print_str(),
                         debug_4_ppstr)
        self.assertEqual(list(trie.find_all('xabc')),
                         [(0, 1, '(x)'), (1, 2, '(ab)'), (0, 4, '(xabc)')])
        self.assertEqual(trie.replace('xabc'),
                         '(xabc)')
        self.assertEqual(trie.greedy_replace('xabc'),
                         '(x)(ab)c')
        self.assertEqual(list(trie.find_all('xabd')),
                         [(0, 1, '(x)'), (1, 2, '(ab)')])
        self.assertEqual(trie.replace('xabd'),
                         '(x)(ab)d')
        self.assertEqual(trie.greedy_replace('xabd'),
                         '(x)(ab)d')

    def test_debug5(self):
        '''Hand-written test case.'''
        trie = ahocorasick.AhoCorasickTrie()
        trie['ac'] = '(ac)'
        trie['acabx'] = '(acabx)'
        trie['ab'] = '(ab)'
        trie._set_suffix_links()
        debug_5_ppstr = '''<ROOT>
  a (suffix = "")
    ab (value = "(ab)") (suffix = "")
    ac (value = "(ac)") (suffix = "")
      aca (suffix = "a")
        acab (suffix = "ab") (dict_suffix = "ab")
          acabx (value = "(acabx)") (suffix = "")'''
        self.assertEqual(trie.pretty_print_str(),
                         debug_5_ppstr)
        self.assertEqual(list(trie.find_all('acaby')),
                         [(0, 2, '(ac)'), (2, 2, '(ab)')])
        self.assertEqual(trie.replace('acaby'),
                         '(ac)(ab)y')
        self.assertEqual(trie.greedy_replace('acaby'),
                         '(ac)(ab)y')

    def test_debug7(self):
        '''Hand-written test case.'''
        trie = ahocorasick.AhoCorasickTrie()
        trie['r 3'] = 'r_3'
        trie['Rather he'] = 'Rather_he'
        trie['er Rabbit'] = 'er_Rabbit'
        trie['a Merry'] = 'a_Merry'
        trie._set_suffix_links()
        debug_7_ppstr = '''<ROOT>
  R (suffix = "")
    Ra (suffix = "a")
      Rat (suffix = "")
        Rath (suffix = "")
          Rathe (suffix = "e")
            Rather (suffix = "er")
              Rather  (suffix = "er ")
                Rather h (suffix = "")
                  Rather he (value = "Rather_he") (suffix = "e")
  a (suffix = "")
    a  (suffix = "")
      a M (suffix = "")
        a Me (suffix = "e")
          a Mer (suffix = "er")
            a Merr (suffix = "r")
              a Merry (value = "a_Merry") (suffix = "")
  e (suffix = "")
    er (suffix = "r")
      er  (suffix = "r ")
        er R (suffix = "R")
          er Ra (suffix = "Ra")
            er Rab (suffix = "")
              er Rabb (suffix = "")
                er Rabbi (suffix = "")
                  er Rabbit (value = "er_Rabbit") (suffix = "")
  r (suffix = "")
    r  (suffix = "")
      r 3 (value = "r_3") (suffix = "")'''
        self.assertEqual(trie.pretty_print_str(), debug_7_ppstr)

    def test_debug8(self):
        '''Hand-written test case.'''
        trie = ahocorasick.AhoCorasickTrie()
        trie['cart'] = '(cart)'
        trie['cat'] = '(cat)'
        self.assertEqual(trie.greedy_replace('carry cat cat carcat cart car'),
                         'carry (cat) (cat) car(cat) (cart) car')
        trie = ahocorasick.AhoCorasickTrie()
        trie[ahocorasick.boundary_transform('dog')] = '(dog)'
        trie[ahocorasick.boundary_transform('ca')] = '(ca)'
        trie[ahocorasick.boundary_transform('cat')] = '(cat)'
        self.assertEqual(''.join(ahocorasick.boundary_untransform(
            trie.greedy_replace(ahocorasick.boundary_transform('my dog is a ca catty cat cat')))),
                         'my (dog) is a (ca) catty (cat) (cat)')


if __name__ == '__main__':
    unittest.main()
