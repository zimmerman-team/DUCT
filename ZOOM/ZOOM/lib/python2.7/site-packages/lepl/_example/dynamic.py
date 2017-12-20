
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,R0201,R0903
#@PydevCodeAnalysisIgnore
# (the code style is for documentation, not "real")

'''
Match opening and cloising tags (a request on the mailing list).
'''

from logging import basicConfig, INFO
from lepl import *
from lepl._example.support import Example


#basicConfig(level=INFO)


class DynamicExample(Example):
    
    def parser(self):
            
        def line(matcher):
            '''Include space before and a newline after'''
            return ~Space()[:] & matcher & ~Space()[:] & ~Literal('\n')
        
        @trampoline_matcher_factory()
        def make_pair(start, end, contents):
            '''Generate a matcher that checks start and end tags.
               `start` must match the start and return the "label"
               `end` must match the end and return the same "label"
               If end fails then contents is used instead (and the matcher
               repeats.
               The return value is a pair that contains the label and 
               the contents.''' 
            def matcher(support, stream0):
                (match, stream1) = yield start._match(stream0)
                label = match[0]
                result = []
                while True:
                    # can we end?
                    try:
                        (match, stream2) = yield end._match(stream1)
                        if match:
                            if match[0] == label:
                                yield ([(label, result)], stream2)
                                return
                            else:
                                support._info('end matched, but %s != %s' % (match[0], label))
                    except StopIteration:
                        support._info('failed to match end')
                        pass
                    # failed to end, so try matching contents instead
                    (match, stream2) = yield contents._match(stream1)
                    result += match
                    support._info('matched %s: %s' % (match, result))
                    stream1 = stream2
            return matcher
                    
        nested = Delayed()
        
        start = line(~Literal('*') & Word())
        end = line(~Literal('*end*') & Word())
        # also, nested must go first here, or we match *bar as data
        contents = nested | line(Word()[:,~Space()[:]])
        
        nested += make_pair(start, end, contents)
    
        return nested.parse
    
    
    def test_all(self):
        
        parse = self.parser()
        
        self.examples([
    
(lambda: parse('*foo\n*end*foo\n'), [('foo', [])]),
    
(lambda: parse(
'''*foo
ab c
*end*foo
'''), [('foo', ['ab', 'c'])]),

# multiple lines
(lambda: parse(
'''*foo
ab c
 p q rs tu
*end*foo
'''), [('foo', ['ab', 'c', 'p', 'q', 'rs', 'tu'])]),
    
(lambda: parse(
'''*foo
ab c
 *bar
 p q rs tu
 *end*bar
*end*foo
'''), [('foo', ['ab', 'c', ('bar', ['p', 'q', 'rs', 'tu'])])]),
    
(lambda: parse(
'''*foo
ab c
 *bar
 p q rs tu
 *end*bar
 pap
*end*foo
'''), [('foo', ['ab', 'c', ('bar', ['p', 'q', 'rs', 'tu']), 'pap'])]),
    
# this is consistent, but perhaps not expected.  if you don't want this, then
# you need to define contents more carefully - perhaps exclude '*' from the
# characters in Word() for example.
(lambda: parse(
'''*foo
ab c
 *bar
 p q rs tu
 *end*baz
*end*foo
'''), [('foo', ['ab', 'c', '*bar', 'p', 'q', 'rs', 'tu', '*end*baz'])])])
        
    

