from lepl.matchers.variables import TraceVariables
from lepl.lexer.matchers import Token
from lepl.support.list import List

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
Tests for cloning matchers.
'''

from unittest import TestCase
from difflib import Differ

from lepl.matchers.core import Literal, Delayed
from lepl.matchers.derived import Drop, UnsignedReal, Optional
from lepl.core.rewriters import clone_matcher


class CloneTest(TestCase):
    
    def assert_clone_ok(self, matcher):
        copy = clone_matcher(matcher)
        mtree = matcher.tree()
        ctree = copy.tree()
        if mtree != ctree:
            print(mtree)
            print(ctree)
            diff = Differ()
            print('\n'.join(diff.compare(mtree.split('\n'), ctree.split('\n'))))
        assert mtree == ctree
        assert matcher is not copy

    def test_single(self):
        self.assert_clone_ok(Literal('foo'))

    def test_no_loop(self):
        self.assert_clone_ok(Literal('a') | 'b' & Drop('c'))
        
    def test_delayed(self):
        d = Delayed()
        d += Literal('foo')
        self.assert_clone_ok(d)
        self.assert_clone_ok(Literal('bar') & d)
    
    def test_loop(self):
        d = Delayed()
        a = d | 'b'
        d += a
        self.assert_clone_ok(d)
        
    def test_loops(self):
        with TraceVariables():
            value = Token(UnsignedReal())
            symbol = Token('[^0-9a-zA-Z \t\r\n]')
            number = (Optional(symbol('-')) + value) >> float
            group2, group3c = Delayed(), Delayed()
    
            parens = symbol('(') & group3c & symbol(')')
            group1 = parens | number
    
            mul = (group2 & symbol('*') & group2) > List     # changed
            div = (group2 & symbol('/') & group2) > List     # changed
            group2 += (mul | div | group1)
    
            add = (group3c & symbol('+') & group3c) > List   # changed
            sub = (group3c & symbol('-') & group3c) > List   # changed
            group3c += (add | sub | group2)
        self.assert_clone_ok(group3c)
        
        
