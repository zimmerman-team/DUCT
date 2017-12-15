
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
Tests for the lepl.core.config module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase
    

from lepl.matchers.variables import TraceVariables
from lepl.matchers.operators import DroppedSpace
from lepl.matchers.derived import Drop, Word, String
from lepl.matchers.core import Any, Lookahead
from lepl._test.base import assert_str
from lepl.stream.maxdepth import FullFirstMatchException
from lepl.regexp.core import RegexpError
from lepl.support.lib import StringIO


class ParseTest(TestCase):
    
    def run_test(self, name, text, parse, match2, match3, error, 
                 config=lambda x: None, **kargs):
        matcher = Any()[:, ...]
        config(matcher)
        parser = getattr(matcher, 'parse' + name)
        result = str(parser(text, **kargs))
        assert_str(result, parse)
        matcher = Any()[2, ...]
        matcher.config.no_full_first_match()
        config(matcher)
        parser = getattr(matcher, 'match' + name)
        result = str(list(parser(text, **kargs)))
        assert_str(result, match2)
        matcher = Any()[3, ...]
        matcher.config.no_full_first_match()
        config(matcher)
        parser = getattr(matcher, 'match' + name)
        result = str(list(parser(text, **kargs)))
        assert_str(result, match3)
        matcher = Any()
        config(matcher)
        parser = getattr(matcher, 'parse' + name)
        try:
            parser(text, **kargs)
        except FullFirstMatchException as e:
            assert_str(e, error)
            
    def test_string(self):
        self.run_test('_string', 'abc', 
                      "['abc']", 
                      "[(['ab'], (2, <helper>))]", 
                      "[(['abc'], (3, <helper>))]", 
                      "The match failed in <string> at 'bc' (line 1, character 2).")
        self.run_test('', 'abc', 
                      "['abc']", 
                      "[(['ab'], (2, <helper>))]", 
                      "[(['abc'], (3, <helper>))]",
                      "The match failed in <string> at 'bc' (line 1, character 2).")
        self.run_test('_sequence', 'abc', 
                      "['abc']", 
                      "[(['ab'], (2, <helper>))]", 
                      "[(['abc'], (3, <helper>))]",
                      "The match failed in <str> at 'bc' (offset 1, value 'b').")

    def test_string_list(self):
        self.run_test('_list', ['a', 'b', 'c'], 
                      "[['a', 'b', 'c']]", 
                      "[([['a', 'b']], (2, <helper>))]", 
                      "[([['a', 'b', 'c']], (3, <helper>))]",
                      "The match failed in <list<str>> at ['b', 'c'] (offset 1, value 'b').", 
                      config=lambda m: m.config.no_compile_to_regexp())
        
    def test_int_list(self):
        #basicConfig(level=DEBUG)
        try:
            # this fails for python2 because it relies on 
            # comparison between types failing
            self.run_test('_list', [1, 2, 3], [], [], [], """""")
        except RegexpError as e:
            assert 'no_compile_to_regexp' in str(e), str(e)
        self.run_test('_list', [1, 2, 3], 
                      "[[1, 2, 3]]", 
                      "[([[1, 2]], (2, <helper>))]", 
                      "[([[1, 2, 3]], (3, <helper>))]",
                      "The match failed in <list<int>> at [2, 3] (offset 1, value 2).",
config=lambda m: m.config.no_compile_to_regexp())


class BugTest(TestCase):
    
    def test_bug(self):
        matcher = Any('a')
        matcher.config.clear()
        result = list(matcher.match_list(['b']))
        assert result == [], result


class TraceVariablesTest(TestCase):
    
    def test_trace(self):
        buffer = StringIO()
        with TraceVariables(out=buffer):
            word = ~Lookahead('OR') & Word()
            phrase = String()
            with DroppedSpace():
                text = (phrase | word)[1:] > list
                query = text[:, Drop('OR')]
        expected = '''      phrase failed                             stream = 'spicy meatballs OR...
        word = ['spicy']                        stream = ' meatballs OR "el ...
      phrase failed                             stream = 'meatballs OR "el b...
        word = ['meatballs']                    stream = ' OR "el bulli rest...
      phrase failed                             stream = 'OR "el bulli resta...
        word failed                             stream = 'OR "el bulli resta...
      phrase failed                             stream = ' OR "el bulli rest...
        word failed                             stream = ' OR "el bulli rest...
        text = [['spicy', 'meatballs']]         stream = ' OR "el bulli rest...
      phrase = ['el bulli restaurant']          stream = ''
      phrase failed                             stream = ''
        word failed                             stream = ''
        text = [['el bulli restaurant']]        stream = ''
       query = [['spicy', 'meatballs'], ['el... stream = ''
'''
        query.config.auto_memoize(full=True)
        query.parse('spicy meatballs OR "el bulli restaurant"')
        trace = buffer.getvalue()
        assert trace == expected, '"""' + trace + '"""'
        # check caching works
        query.parse('spicy meatballs OR "el bulli restaurant"')
        trace = buffer.getvalue()
        assert trace == expected, '"""' + trace + '"""'

        