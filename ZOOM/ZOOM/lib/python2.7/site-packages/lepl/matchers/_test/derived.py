from lepl.stream.core import s_next

# The contents of this file are subject to the Mozilla Public License
# (MPL) Version 1.1 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License
# at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
# the License for the specific language governing rights and
# limitations under the License.
#LogMixin
# The Original Code is LEPL (http://www.acooke.org/lepl)
# The Initial Developer of the Original Code is Andrew Cooke.
# Portions created by the Initial Developer are Copyright (C) 2009-2010
# Andrew Cooke (andrew@acooke.org). All Rights Reserved.
#
# Alternatively, the contents of this file may be used under the terms
# of the LGPL license (the GNU Lesser General Public License,
# http://www.gnu.org/licenses/lgpl.html), in which case the provisions
# of the LGPL License are applicable instead of those above.
#
# If you wish to allow use of your version of this file only under the
# terms of the LGPL License and not to allow others to use your version
# of this file under the MPL, indicate your decision by deleting the
# provisions above and replace them with the notice and other provisions
# required by the LGPL License.  If you do not delete the provisions
# above, a recipient may use your version of this file under either the
# MPL or the LGPL License.

'''
Tests for the lepl.matchers.derived module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.matchers.monitor import Trace
from lepl.matchers.derived import Repeat, Space, SkipTo, Newline, String, \
    SkipString, SingleLineString, UnsignedInteger, SignedInteger, \
    UnsignedReal, SignedReal, UnsignedEReal, SignedEReal, UnsignedFloat, \
    SignedFloat, UnsignedEFloat, SignedEFloat, Optional, Add, Reduce, Star
from lepl.stream.maxdepth import FullFirstMatchException
from lepl.matchers.core import Any
from lepl._test.base import BaseTest
from lepl.matchers.support import OperatorMatcher
from lepl.core.parser import tagged
from lepl.support.warn import silence

silence('UnsignedFloat')
silence('SignedFloat')
silence('UnsignedEFloat')
silence('SignedEFloat')

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, R0201, R0913, R0901, R0904
# (dude this is just a test)

class RepeatTest(TestCase):

    def test_simple(self):
        #basicConfig(level=DEBUG)
        self.assert_simple([1], 1, 1, 'd', ['0'])
        self.assert_simple([1], 1, 2, 'd', ['0'])
        self.assert_simple([2], 1, 1, 'd', ['0','1'])
        self.assert_simple([2], 1, 2, 'd', ['0','1'])
        self.assert_simple([2], 0, 2, 'd', ['0','1',''])
        self.assert_simple([1,2], 1, 1, 'd', ['0'])
        self.assert_simple([1,2], 1, 2, 'd', ['00','01','0'])
        self.assert_simple([1,2], 2, 2, 'd', ['00','01'])
        self.assert_simple([1,2], 1, 2, 'b', ['0','00','01'])
        self.assert_simple([1,2], 1, 2, 'g', ['00','01','0'])

    def assert_simple(self, stream, start, stop, algorithm, target):
        matcher = Repeat(RangeMatch(), start, stop, algorithm=algorithm)
        matcher.config.no_full_first_match()
        result = list(matcher.match_list(stream))
        #print(result)
        result = [''.join(map(str, l)) for (l, _s) in result]
        assert target == result, result
        
    def test_mixin(self):
        #basicConfig(level=DEBUG)
        r = RangeMatch()
        self.assert_mixin(r[1:1], [1], ['0'])
        self.assert_mixin(r[1:2], [1], ['0'])
        self.assert_mixin(r[1:1], [2], ['0','1'])
        self.assert_mixin(r[1:2], [2], ['0','1'])
        self.assert_mixin(r[0:], [2], ['0','1', ''])
        self.assert_mixin(r[:], [2], ['0','1', ''])
        self.assert_mixin(r[0:2], [2], ['0','1', ''])
        self.assert_mixin(r[1], [1,2], ['0'])
        self.assert_mixin(r[1:2], [1,2], ['00','01', '0'])
        self.assert_mixin(r[2], [1,2], ['00','01'])
        self.assert_mixin(r[1:2:'b'], [1,2], ['0', '00','01'])
        self.assert_mixin(r[1:2:'d'], [1,2], ['00', '01','0'])
        try:        
            self.assert_mixin(r[1::'x'], [1,2,3], [])
            assert False, 'expected error'
        except KeyError:
            pass
    
    def assert_mixin(self, match, stream, target):
        match.config.no_full_first_match()
        result = [''.join(map(str, l)) 
                  for (l, _s) in match.match_list(stream)]
        assert target == result, result
       
    def test_separator(self):
        #basicConfig(level=DEBUG)
        self.assert_separator('a', 1, 1, 'd', ['a'])
        self.assert_separator('a', 1, 1, 'b', ['a'])
        self.assert_separator('a,a', 1, 2, 'd', ['a,a', 'a'])
        self.assert_separator('a,a', 1, 2, 'b', ['a', 'a,a'])
        self.assert_separator('a,a,a,a', 2, 3, 'd', ['a,a,a', 'a,a'])
        self.assert_separator('a,a,a,a', 2, 3, 'b', ['a,a', 'a,a,a'])
        
    def assert_separator(self, stream, start, stop, algorithm, target):
        matcher = Repeat(Any('abc'), start, stop, 
                         algorithm=algorithm, separator=Any(','))
        matcher.config.no_full_first_match()
        result = [''.join(l) 
                  for (l, _s) in matcher.match_string(stream)]
        assert target == result, result
        
    def test_separator_mixin(self):
        #basicConfig(level=DEBUG)
        abc = Any('abc')
        self.assert_separator_mixin(abc[1:1:'d',','], 'a', ['a'])
        self.assert_separator_mixin(abc[1:1:'b',','], 'a', ['a'])
        self.assert_separator_mixin(abc[1:2:'d',','], 'a,b', ['a,b', 'a'])
        self.assert_separator_mixin(abc[1:2:'b',','], 'a,b', ['a', 'a,b'])
        self.assert_separator_mixin(abc[2:3:'d',','], 'a,b,c,a', ['a,b,c', 'a,b'])
        self.assert_separator_mixin(abc[2:3:'b',','], 'a,b,c,a', ['a,b', 'a,b,c'])

    def assert_separator_mixin(self, matcher, stream, target):
        matcher.config.no_full_first_match()
        result = [''.join(map(str, l)) for (l, _s) in matcher.match_string(stream)]
        assert target == result, result
    
    
class RangeMatch(OperatorMatcher):
    '''
    We test repetition by looking at "strings" of integers, where the 
    matcher for any particular value returns all values less than the
    current value. 
    '''
    
    def __init__(self):
        super(RangeMatch, self).__init__()
    
    @tagged
    def _match(self, stream):
        (value, next_stream) = s_next(stream)
        for i in range(value[0]):
            yield ([i], next_stream)


class AddReduceTest(BaseTest):

    def test_add(self):
        self.assert_direct('123', Add(Star(Any())), [['123'], ['12'], ['1'], []])

    def test_reduce(self):
        self.assert_direct('123', Reduce(Star(Any()), ''), [['123'], ['12'], ['1'], ['']])


class SpaceTest(BaseTest):
    
    def test_space(self):
        self.assert_direct('  ', Space(), [[' ']])
        self.assert_direct('  ', Space()[0:], [[' ', ' '], [' '], []])
        self.assert_direct('  ', Space()[0:,...], [['  '], [' '], []])
        
    def test_slash(self):
        ab = Any('ab')
        self.assert_direct('ab', ab / ab, [['a', 'b']])
        self.assert_direct('a b', ab / ab, [['a', ' ', 'b']])
        self.assert_direct('a  b', ab / ab, [['a', '  ', 'b']])
        self.assert_direct('ab', ab // ab, [])
        self.assert_direct('a b', ab // ab, [['a', ' ', 'b']])
        self.assert_direct('a  b', ab // ab, [['a', '  ', 'b']])

 
class SkipToTest(BaseTest):
    
    def test_skip(self):
        self.assert_direct('aabcc', SkipTo('b'), [['aab']])
        self.assert_direct('aabcc', SkipTo('b', False), [['aa']])
    
    def test_next_line(self):
        #basicConfig(level=DEBUG)
        self.assert_direct('''abc
d''', Trace(~SkipTo(Newline()) + 'd'), [['d']])


class StringTest(BaseTest):
    
    def test_simple(self):
        self.assert_direct('"abc"', String(), [['abc']])
        self.assert_direct('"abc"d', String(), [['abc']])
        self.assert_direct('"abc"', SingleLineString(), [['abc']])
        self.assert_direct('"abc"d', SingleLineString(), [['abc']])
        self.assert_direct('"abc"', SkipString(), [['abc']])
        self.assert_direct('"abc"d', SkipString(), [['abc']])

    def test_empty(self):
        self.assert_direct('""', String(), [['']])
        self.assert_direct("''", String(quote="'"), [['']])

    def test_escape(self):
        self.assert_direct('"ab\\"c"', String(), [['ab"c'], ['ab\\']])
        
    def test_multiple_lines(self):
        self.assert_direct('"ab\nc"', String(), [['ab\nc']])
        self.assert_direct('"ab\nc"', SingleLineString(), [])
        self.assert_direct('"ab\nc"', SkipString(), [['abc']])

    def test_ints(self):
        self.assert_direct([1,2,3,1], String(quote=[1], empty=[]), [[[2,3]]])


class OptionalTest(BaseTest):
    
    def test_optional(self):
        self.assert_direct('a', Optional('a'), [['a'], []])


class NumberTest(BaseTest):
    
    def do_test(self, matcher, good, bad):
        def test(value, ok):
            try:
                matcher.parse(value)
                assert ok, value
            except FullFirstMatchException:
                assert not ok, value
        for value in good: test(value, True)
        for value in bad: test(value, False)
        
    def test_numbers(self):
        self.do_test(UnsignedInteger(),
                     ['1'], 
                     ['-1', 
                      '1.', '-1.', 
                      '1.2', '-1.2', 
                      '1e3', '-1e3', '1e-3', '-1e-3',
                      '1.e3', '-1.e3', '1.e-3', '-1.e-3',
                      '1.2e3', '-1.2e3', '1.2e-3', '-1.2e-3'])
        self.do_test(SignedInteger(),
                     ['1', '-1'], 
                     ['1.', '-1.', 
                      '1.2', '-1.2', 
                      '1e3', '-1e3', '1e-3', '-1e-3',
                      '1.e3', '-1.e3', '1.e-3', '-1.e-3',
                      '1.2e3', '-1.2e3', '1.2e-3', '-1.2e-3'])
        self.do_test(UnsignedReal(),
                     ['1', '1.', '1.2'],
                     ['-1', '-1.', '-1.2', 
                      '1e3', '-1e3', '1e-3', '-1e-3',
                      '1.e3', '-1.e3', '1.e-3', '-1.e-3',
                      '1.2e3', '-1.2e3', '1.2e-3', '-1.2e-3'])
        self.do_test(SignedReal(),
                     ['1', '-1', 
                      '1.', '-1.', 
                      '1.2', '-1.2'], 
                     ['1e3', '-1e3', '1e-3', '-1e-3',
                      '1.e3', '-1.e3', '1.e-3', '-1.e-3',
                      '1.2e3', '-1.2e3', '1.2e-3', '-1.2e-3'])
        self.do_test(UnsignedEReal(),
                     ['1', '1.', '1.2', 
                      '1e3', '1e-3', '1.e3', '1.e-3', 
                      '1.2e3', '1.2e-3'],
                     ['-1', '-1.', '-1.2', 
                      '-1e3', '-1e-3', '-1.e3', '-1.e-3', 
                      '-1.2e3', '-1.2e-3'])
        self.do_test(SignedEReal(),
                     ['1', '1.', '1.2', 
                      '1e3', '1e-3', '1.e3', '1.e-3', 
                      '1.2e3', '1.2e-3',
                      '-1', '-1.', '-1.2', 
                      '-1e3', '-1e-3', '-1.e3', '-1.e-3', 
                      '-1.2e3', '-1.2e-3'],
                      [])
        self.do_test(UnsignedFloat(),
                     ['1.', '1.2'],
                     ['1', '-1', '-1.', '-1.2', 
                      '1e3', '-1e3', '1e-3', '-1e-3',
                      '1.e3', '-1.e3', '1.e-3', '-1.e-3',
                      '1.2e3', '-1.2e3', '1.2e-3', '-1.2e-3'])
        self.do_test(SignedFloat(),
                     ['1.', '-1.', 
                      '1.2', '-1.2'], 
                     ['1', '-1', 
                      '1e3', '-1e3', '1e-3', '-1e-3',
                      '1.e3', '-1.e3', '1.e-3', '-1.e-3',
                      '1.2e3', '-1.2e3', '1.2e-3', '-1.2e-3'])
        self.do_test(UnsignedEFloat(),
                     ['1.', '1.2', 
                      '1e3', '1e-3', '1.e3', '1.e-3', 
                      '1.2e3', '1.2e-3'],
                     ['1', '-1', '-1.', '-1.2', 
                      '-1e3', '-1e-3', '-1.e3', '-1.e-3', 
                      '-1.2e3', '-1.2e-3'])
        self.do_test(SignedEFloat(),
                     ['1.', '1.2',
                      '1e3', '1e-3', '1.e3', '1.e-3', 
                      '1.2e3', '1.2e-3',
                      '-1.', '-1.2', 
                      '-1e3', '-1e-3', '-1.e3', '-1.e-3', 
                      '-1.2e3', '-1.2e-3'],
                      ['1', '-1'])
        