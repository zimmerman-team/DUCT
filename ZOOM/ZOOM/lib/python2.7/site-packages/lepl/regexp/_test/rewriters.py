from lepl.stream.core import DUMMY_HELPER

# The contents of this file are subject to the Mozilla Public License
# (MPL) Version 1.1 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License
# at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
# the License for the specific language governing rights and
# limitations under the License.
#
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
Tests for the lepl.regexp.rewriters module.
'''

from logging import basicConfig, DEBUG
from string import ascii_letters
from unittest import TestCase

from lepl import *
from lepl.regexp.rewriters import CompileRegexp

# pylint: disable-msg=C0103, C0111, C0301, C0324
# (dude this is just a test)


class RewriteTest(TestCase):
    
    def test_any(self):
        #basicConfig(level=DEBUG)
        char = Any()
        
        char.config.clear().compile_to_nfa(force=True).no_memoize()
        matcher = char.get_match_sequence()
        results = list(matcher('abc'))
        assert results == [(['a'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp)
        
        char.config.clear().compile_to_nfa(force=True).compose_transforms().no_memoize()
        matcher = char.get_match_sequence()
        results = list(matcher('abc'))
        assert results == [(['a'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp)
        
    def test_or(self):
        #basicConfig(level=DEBUG)
        rx = Any('a') | Any('b') 
        
        rx.config.clear().compile_to_nfa(force=True).no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('bq'))
        assert results == [(['b'], (1, DUMMY_HELPER))], results
        results = list(matcher('aq'))
        assert results == [(['a'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp)
        
        rx.config.clear().compile_to_nfa(force=True).compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('bq'))
        assert results == [(['b'], (1, DUMMY_HELPER))], results
        results = list(matcher('aq'))
        assert results == [(['a'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp)
        
    def test_plus(self):
        rx = Any('a') + Any('b') 
        
        rx.config.clear().compile_to_nfa(force=True).no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('abq'))
        assert results == [(['ab'], (2, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
        rx.config.clear().compile_to_nfa(force=True).compose_transforms()
        matcher = rx.get_match_sequence()
        results = list(matcher('abq'))
        assert results == [(['ab'], (2, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
    def test_add(self):
        rx = Add(And(Any('a'), Any('b'))) 
        
        rx.config.clear().compile_to_nfa(force=True).no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('abq'))
        assert results == [(['ab'], (2, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        rx.config.clear().compile_to_nfa(force=True).compose_transforms()
        
        matcher = rx.get_match_sequence()
        results = list(matcher('abq'))
        assert results == [(['ab'], (2, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
    def test_literal(self):
        rx = Literal('abc')
        
        rx.config.clear().compile_to_nfa(force=True).no_memoize()
        matcher = rx.get_match_sequence()
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        results = list(matcher('abcd'))
        assert results == [(['abc'], (3, DUMMY_HELPER))], results
        
        rx.config.clear().compile_to_nfa(force=True).compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        results = list(matcher('abcd'))
        assert results == [(['abc'], (3, DUMMY_HELPER))], results
        
        rx = Literal('abc') >> (lambda x: x+'e')
        
        rx.config.clear().compile_to_nfa(force=True).no_memoize()
        matcher = rx.get_match_sequence()
        print(matcher.matcher.tree())
        results = list(matcher('abcd'))
        assert results == [(['abce'], (3, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
        rx.config.clear().compile_to_nfa(force=True).compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        print(matcher.matcher.tree())
        results = list(matcher('abcd'))
        assert results == [(['abce'], (3, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
    def test_dfs(self):
        expected = [(['abcd'], (4, DUMMY_HELPER)), 
                    (['abc'], (3, DUMMY_HELPER)), 
                    (['ab'], (2, DUMMY_HELPER)), 
                    (['a'], (1, DUMMY_HELPER)),
                    ([], (0, DUMMY_HELPER))]
        rx = Any()[:, ...]
        
        # do un-rewritten to check whether [] or [''] is correct
        rx.config.clear().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('abcd'))
        assert results == expected, results
        
        rx.config.clear().compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('abcd'))
        assert results == expected, results
        
        #basicConfig(level=DEBUG)
        rx.config.clear().compile_to_nfa().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('abcd'))
        assert results == expected, results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
        rx.config.clear().compile_to_nfa().compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('abcd'))
        assert results == expected, results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
    
    def test_complex(self):
        #basicConfig(level=DEBUG)
        rx = Literal('foo') | (Literal('ba') + Any('a')[1:,...])
        
        rx.config.compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        results = list(matcher('foo'))
        assert results == [(['foo'], (3, DUMMY_HELPER))], results
        results = list(matcher('baaaaax'))
        assert results == [(['baaaaa'], (6, DUMMY_HELPER)), 
                           (['baaaa'], (5, DUMMY_HELPER)), 
                           (['baaa'], (4, DUMMY_HELPER)), 
                           (['baa'], (3, DUMMY_HELPER))], results
        results = list(matcher('ba'))
        assert results == [], results
        
        rx.config.clear().compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        results = list(matcher('foo'))
        assert results == [(['foo'], (3, DUMMY_HELPER))], results
        results = list(matcher('baaaaax'))
        assert results == [(['baaaaa'], (6, DUMMY_HELPER)), 
                           (['baaaa'], (5, DUMMY_HELPER)), 
                           (['baaa'], (4, DUMMY_HELPER)), 
                           (['baa'], (3, DUMMY_HELPER))], results
        results = list(matcher('ba'))
        assert results == [], results
        
        rx.config.clear().compile_to_nfa().no_full_first_match().compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        results = list(matcher('foo'))
        assert results == [(['foo'], (3, DUMMY_HELPER))], results
        results = list(matcher('baaaaax'))
        assert results == [(['baaaaa'], (6, DUMMY_HELPER)), 
                           (['baaaa'], (5, DUMMY_HELPER)), 
                           (['baaa'], (4, DUMMY_HELPER)), 
                           (['baa'], (3, DUMMY_HELPER))], results
        results = list(matcher('ba'))
        assert results == [], results

    def test_integer(self):
        rx = Integer()
        
        rx.config.compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('12x'))
        assert results == [(['12'], (2, DUMMY_HELPER)), (['1'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()

        rx.config.clear().compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('12x'))
        assert results == [(['12'], (2, DUMMY_HELPER)), (['1'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()

        rx.config.clear().compile_to_nfa().no_full_first_match().compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('12x'))
        assert results == [(['12'], (2, DUMMY_HELPER)), (['1'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
    def test_real(self):
        rx = Real()
        
        rx.config.compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('1.2x'))
        assert results == [(['1.2'], (3, DUMMY_HELPER)), (['1.'], (2, DUMMY_HELPER)), (['1'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()

        rx.config.clear().compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('1.2x'))
        assert results == [(['1.2'], (3, DUMMY_HELPER)), (['1.'], (2, DUMMY_HELPER)), (['1'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()

        rx.config.clear().compile_to_nfa().no_full_first_match().compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('1.2x'))
        assert results == [(['1.2'], (3, DUMMY_HELPER)), (['1.'], (2, DUMMY_HELPER)), (['1'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
    def test_float(self):
        rx = Float()
        
        rx.config.compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('1.2x'))
        assert results == [(['1.2'], (3, DUMMY_HELPER)), (['1.'], (2, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()

        rx.config.clear().compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('1.2x'))
        assert results == [(['1.2'], (3, DUMMY_HELPER)), (['1.'], (2, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree().no_memoize()

        rx.config.clear().compile_to_nfa().no_full_first_match().compose_transforms()
        matcher = rx.get_match_sequence()
        results = list(matcher('1.2x'))
        assert results == [(['1.2'], (3, DUMMY_HELPER)), (['1.'], (2, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree().no_memoize()
        
    def test_star(self):
        rx = Add(Star('a')) 
        
        rx.config.compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('aa'))
        assert results == [(['aa'], (2, DUMMY_HELPER)), (['a'], (1, DUMMY_HELPER)), ([], (0, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
        rx.config.clear().compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('aa'))
        assert results == [(['aa'], (2, DUMMY_HELPER)), (['a'], (1, DUMMY_HELPER)), ([], (0, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
        rx.config.clear().compile_to_nfa().no_full_first_match().compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('aa'))
        assert results == [(['aa'], (2, DUMMY_HELPER)), (['a'], (1, DUMMY_HELPER)), ([], (0, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
    def test_word(self):
        #basicConfig(level=DEBUG)
        rx = Word('a')
        
        rx.config.compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('aa'))
        assert results == [(['aa'], (2, DUMMY_HELPER)), (['a'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
        rx.config.clear().compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('aa'))
        assert results == [(['aa'], (2, DUMMY_HELPER)), (['a'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
        rx.config.clear().compile_to_nfa().no_full_first_match().compose_transforms().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('aa'))
        assert results == [(['aa'], (2, DUMMY_HELPER)), (['a'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        

class CompileTest(TestCase):
    '''
    Test the rewrite routine directly.
    '''
    
    def assert_regexp(self, matcher, regexp):
        compiler = CompileRegexp(use=True)
        matcher = compiler(matcher)
        assert isinstance(matcher, NfaRegexp), matcher.tree()
        assert str(matcher.regexp) == regexp, matcher.regexp
    
    def test_any(self):
        self.assert_regexp(Any(), '.')
        self.assert_regexp(Any('abc'), '[a-c]')
    
    def test_literal(self):
        self.assert_regexp(Literal('foo'), 'foo')

    def test_repeat(self):
        self.assert_regexp(Any()[:, ...], '(?:.)*')
        self.assert_regexp(Any()[1:, ...], '.(?:.)*')
        self.assert_regexp(Any()[1, ...], '.')
        self.assert_regexp(Any()[1:2, ...], '.(?:.)?')
        self.assert_regexp(Any()[2, ...], '..')
        self.assert_regexp(Any()[2:4, ...], '..(?:.(?:.)?)?')
        self.assert_regexp(Any()[:, 'x', ...], '(?:.(?:x.)*|)')
        self.assert_regexp(Any()[1:, 'x', ...], '.(?:x.)*')
        self.assert_regexp(Any()[1, 'x', ...], '.')
        self.assert_regexp(Any()[1:2, 'x', ...], '.(?:x.)?')
        self.assert_regexp(Any()[2, 'x', ...], '.x.')
        self.assert_regexp(Any()[2:4, 'x', ...], '.x.(?:x.(?:x.)?)?')
        self.assert_regexp(Literal('foo')[:, ...], '(?:foo)*')

    def test_and(self):
        self.assert_regexp(Any('ab')[:, ...] + Any('p'), '(?:[a-b])*p')
        
    def test_or(self):
        self.assert_regexp(Any('ab')[:, ...] | Any('p'), '(?:(?:[a-b])*|p)')

    def test_complex(self):
        self.assert_regexp((Any('ab') + Literal('q')) | Literal('z'), '(?:[a-b]q|z)')
        self.assert_regexp((Any('ab') + 'q') | 'z', '(?:[a-b]q|z)')
        
        
class RepeatBugTest(TestCase):
    
    def test_bug(self):
        #basicConfig(level=DEBUG)
        matcher = Any()[2, ...]
        matcher.config.no_full_first_match().compile_to_nfa()
        parser = matcher.get_parse_all()
        results = list(parser('abc'))
        assert results == [['ab']], results
        
    def test_bug2(self):
        matcher = NfaRegexp('..')
        matcher.config.no_full_first_match()
        parser = matcher.get_parse_all()
        results = list(parser('abc'))
        assert results == [['ab']], results


class WordBugTest(TestCase):
    '''
    Used to not be possible to compile a raw Word() 
    '''
    
    def test_word(self):
        #basicConfig(level=DEBUG)
        rx = Word()
        
        rx.config.compile_to_nfa().no_full_first_match().no_memoize()
        matcher = rx.get_match_sequence()
        results = list(matcher('aa'))
        assert results == [(['aa'], (2, DUMMY_HELPER)), (['a'], (1, DUMMY_HELPER))], results
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()


class TokenBugTest(TestCase):
    '''
    Token(Word()) and Token(Any(ascii_letters)[1:]) gave errors.
    '''
    
    def test_token_word(self):
        tk = Token(Word())
        tk.config.lines(block_policy=explicit)
        tk.get_parse()
        
    def test_token_any(self):
        tk = Token(Any(ascii_letters)[1:,...])
        tk.config.lines(block_policy=explicit)
        tk.get_parse()
    
    def test_simple_word(self):
        #basicConfig(level=DEBUG)
        rx = Word()
        rx.config.no_memoize()
        matcher = rx.get_parse().matcher
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        
    def test_simple_any(self):
        rx = Any(ascii_letters)[1:,...]
        rx.config.compile_to_nfa().no_memoize()
        matcher = rx.get_parse().matcher
        assert isinstance(matcher.matcher, NfaRegexp), matcher.matcher.tree()
        