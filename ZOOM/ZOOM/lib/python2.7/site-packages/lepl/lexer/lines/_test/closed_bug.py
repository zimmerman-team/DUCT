
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
Tests related to a now-forgotten bug. 
'''

from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *


class ClosedBugTest(TestCase):
    
    def test_as_given(self):
        empty = ~Line(Empty(), indent=False)
        word = Token(Word())
        comment = ~Line(Token('#.*'), indent=False)
        CLine = ContinuedLineFactory(Token(r'\\'))
        token = word[1:]
        block = Delayed()
        line = ((CLine(token) | block) > list) | empty | comment
        block += CLine((token)) & Block(line[:])
        program = (line[:] & Eos())
        program.config.lines(block_policy=explicit)
        self.run_test(program.get_parse(), False)

    def test_fixed(self):
        #basicConfig(level=DEBUG)
        empty = ~Line(Empty(), indent=False)
        word = Token(Word())
        text = word[1:]
        block = Delayed()
        line = Line(text) | block | empty
        block += empty | (Block(line[1:]) > list)
        program = Trace(block[:] & Eos())
        program.config.lines(block_policy=to_right, block_start=-1)
        self.run_test(program.get_parse(), True)
        
    def run_test(self, parser, ok):
        try:
            result = parser("""
a1
a2
    b2
        c2
    b2
   
    b2
        c2
                
           d2
            e2
    b2
a3
    b3
a4
""")
            if ok:
                assert result == [['a1', 'a2', ['b2', ['c2'], 'b2', 'b2', ['c2', ['d2', ['e2']]], 'b2'], 'a3', ['b3'], 'a4']], result
        except:
            if ok:
                raise
            ok = True
        if not ok:
            assert False, 'expected error'
            