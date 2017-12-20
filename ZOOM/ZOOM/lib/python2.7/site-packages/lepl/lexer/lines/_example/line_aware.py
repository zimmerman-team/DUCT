
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
Show how line aware parsing can be used.
'''

from unittest import TestCase
from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class LineAwareTest(TestCase):
    
    def test_explicit_start_end(self):
        contents = Token(Any()[:,...]) > list
        line = LineStart() & contents & LineEnd()
        lines = line[:]
        lines.config.lines()
        result = lines.parse('line one\nline two\nline three')
        assert result == [['line one\n'], ['line two\n'], ['line three']], result

    def test_line(self):
        contents = Token(Any()[:,...]) > list
        line = Line(contents)
        lines = line[:]
        lines.config.lines()
        result = lines.parse('line one\nline two\nline three')
        assert result == [['line one\n'], ['line two\n'], ['line three']], result

    def test_continued_line(self):
        contents = Token('[a-z]+')[:] > list
        CLine = ContinuedLineFactory(r'\\')
        line = CLine(contents)
        lines = line[:]
        lines.config.lines()
        result = lines.parse('line one \\\nline two\nline three')
        assert result == [['line', 'one', 'line', 'two'], ['line', 'three']], result
        
    def test_extend(self):
        #basicConfig(level=DEBUG)
        contents = Token('[a-z]+')[:] > list
        parens = Token('\(') & contents & Token('\)') > list
        line = Line(contents & Optional(Extend(parens)))
        lines = line[:]
        lines.config.lines()
        result = lines.parse('line one (this\n extends to line two)\nline three')
        assert result == [['line', 'one'], ['(', ['this', 'extends', 'to', 'line', 'two'], ')'], ['line', 'three']], result
        
    def test_extend_deepest(self):
        '''
        This returned None.
        '''
        #basicConfig(level=DEBUG)
        contents = Token('[a-z]+')[:] > list
        parens = Token('\(') & contents & Token('\)') > list
        line = Line(contents & Optional(Extend(parens)))
        lines = line[:]
        lines.config.lines().record_deepest()
        result = lines.parse('line one (this\n extends to line two)\nline three')
        assert result == [['line', 'one'], ['(', ['this', 'extends', 'to', 'line', 'two'], ')'], ['line', 'three']], result
        
