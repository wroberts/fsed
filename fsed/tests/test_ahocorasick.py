#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test_ahocorasick.py
(c) Will Roberts  12 December, 2015

Unit tests for the ``ahocorasick`` module.
'''


from __future__ import absolute_import, print_function, unicode_literals
from .. import ahocorasick
import doctest
import unittest

def debug1():
    '''
    >>> debug1()
    <ROOT>
      a (value = "(a)")
        ab (value = "(ab)")
      b
        ba
          bab (value = "(bab)")
        bc (value = "(bc)")
          bca (value = "(bca)")
      c (value = "(c)")
        ca
          caa (value = "(caa)")
    '''
    t = ahocorasick.Trie()
    t['a'] = '(a)'
    t['ab'] = '(ab)'
    t['bab'] = '(bab)'
    t['bc'] = '(bc)'
    t['bca'] = '(bca)'
    t['c'] = '(c)'
    t['caa'] = '(caa)'
    t.pretty_print()

def debug2():
    '''
    >>> debug2()
    <ROOT>
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
          dog (value = "(dog)") (suffix = "")
    <ROOT>
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
            ogre (value = "(ogre)") (suffix = "")
    '''
    t = ahocorasick.AhoCorasickTrie()
    t['damn'] = '(damn)'
    t['dog'] = '(dog)'
    t['cat'] = '(cat)'
    t['cablex'] = '(cablex)'
    t._set_suffix_links()
    t.pretty_print()
    t['ogre'] = '(ogre)'
    t._set_suffix_links()
    t.pretty_print()

def debug3():
    '''
    >>> debug3()
    <ROOT>
      a (value = "(a)") (suffix = "")
        ab (value = "(ab)") (suffix = "b")
      b (suffix = "")
        ba (suffix = "a") (dict_suffix = "a")
          bab (value = "(bab)") (suffix = "ab") (dict_suffix = "ab")
        bc (value = "(bc)") (suffix = "c") (dict_suffix = "c")
          bca (value = "(bca)") (suffix = "ca") (dict_suffix = "a")
      c (value = "(c)") (suffix = "")
        ca (suffix = "a") (dict_suffix = "a")
          caa (value = "(caa)") (suffix = "a") (dict_suffix = "a")
    [(0, 1, u'(a)'), (0, 2, u'(ab)'), (1, 2, u'(bc)'), (2, 1, u'(c)'), (3, 1, u'(c)'), (4, 1, u'(a)'), (4, 2, u'(ab)')]
    (a)(bc)(c)(ab)
    (a)(bc)(c)(a)b
    '''
    t = ahocorasick.AhoCorasickTrie()
    t['a'] = '(a)'
    t['ab'] = '(ab)'
    t['bab'] = '(bab)'
    t['bc'] = '(bc)'
    t['bca'] = '(bca)'
    t['c'] = '(c)'
    t['caa'] = '(caa)'
    t._set_suffix_links()
    t.pretty_print()
    print(list(t.find_all('abccab')))
    print(t.replace('abccab'))
    print(t.greedy_replace('abccab'))

def debug4():
    '''
    >>> debug4()
    <ROOT>
      a (suffix = "")
        ab (value = "(ab)") (suffix = "")
      x (value = "(x)") (suffix = "")
        xa (suffix = "a")
          xab (suffix = "ab") (dict_suffix = "ab")
            xabc (value = "(xabc)") (suffix = "")
    [(0, 1, u'(x)'), (1, 2, u'(ab)'), (0, 4, u'(xabc)')]
    (xabc)
    (x)(ab)c
    [(0, 1, u'(x)'), (1, 2, u'(ab)')]
    (x)(ab)d
    (x)(ab)d
    '''
    t = ahocorasick.AhoCorasickTrie()
    t['x'] = '(x)'
    t['xabc'] = '(xabc)'
    t['ab'] = '(ab)'
    t._set_suffix_links()
    t.pretty_print()
    print(list(t.find_all('xabc')))
    print(t.replace('xabc'))
    print(t.greedy_replace('xabc'))
    print(list(t.find_all('xabd')))
    print(t.replace('xabd'))
    print(t.greedy_replace('xabd'))

def debug5():
    '''
    >>> debug5()
    <ROOT>
      a (suffix = "")
        ab (value = "(ab)") (suffix = "")
        ac (value = "(ac)") (suffix = "")
          aca (suffix = "a")
            acab (suffix = "ab") (dict_suffix = "ab")
              acabx (value = "(acabx)") (suffix = "")
    [(0, 2, u'(ac)'), (2, 2, u'(ab)')]
    (ac)(ab)y
    (ac)(ab)y
    '''
    t = ahocorasick.AhoCorasickTrie()
    t['ac'] = '(ac)'
    t['acabx'] = '(acabx)'
    t['ab'] = '(ab)'
    t._set_suffix_links()
    t.pretty_print()
    print(list(t.find_all('acaby')))
    print(t.replace('acaby'))
    print(t.greedy_replace('acaby'))

def debug6():
    '''
    >>> debug6()
    my (dog) is a (ca) catty (cat) (cat)
    '''
    t = ahocorasick.AhoCorasickTrie()
    t['dog'] = '(dog)'
    t['ca'] = '(ca)'
    t['cat'] = '(cat)'
    print(t.greedy_replace_w_sep('my dog is a ca catty cat cat'))

def debug7():
    '''
    >>> debug7()
    <ROOT>
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
          r 3 (value = "r_3") (suffix = "")
    '''
    t = ahocorasick.AhoCorasickTrie()
    t['r 3'] = 'r_3'
    t['Rather he'] = 'Rather_he'
    t['er Rabbit'] = 'er_Rabbit'
    t['a Merry'] = 'a_Merry'
    t._set_suffix_links()
    t.pretty_print()

def debug8():
    '''
    >>> debug8()
    carry (cat) (cat) car(cat) (cart) car
    my (dog) is a (ca) catty (cat) (cat)
    '''
    t = ahocorasick.AhoCorasickTrie()
    t['cart'] = '(cart)'
    t['cat'] = '(cat)'
    print(t.greedy_replace('carry cat cat carcat cart car'))
    t = ahocorasick.AhoCorasickTrie()
    t[ahocorasick.boundary_transform('dog')] = '(dog)'
    t[ahocorasick.boundary_transform('ca')] = '(ca)'
    t[ahocorasick.boundary_transform('cat')] = '(cat)'
    print(''.join(ahocorasick.boundary_untransform(
        t.greedy_replace(ahocorasick.boundary_transform('my dog is a ca catty cat cat')))))


class TestAhocorasick(unittest.TestCase):
    '''
    Unit tests for the `ahocorasick` module.
    '''

    def test_doctest(self):
        '''Run doctests.'''
        self.assertTrue(doctest.testmod(raise_on_error=True))

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


if __name__ == '__main__':
    unittest.main()
