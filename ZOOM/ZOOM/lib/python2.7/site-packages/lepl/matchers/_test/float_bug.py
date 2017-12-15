
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
Tests for a weird bug when writing the float (rational at the time) matcher.

This came down to optional entries being mapped in NFA as empty transitions 
from a single node.  If multiple choices were from the same node the empty
transition order was incorrect (it's ordered by node number, and the node
for the empty transition was created after other nodes, intead of before).

The fix used was to change the node creation order.  Other nodes appear to 
be created correctly.  However, it would be better in the longer term, I
suspect, to use an ordered dict or similar to store the empty transitions
so that the numbering is not needed for order.
'''

#from logging import basicConfig, DEBUG

from lepl.matchers.derived import UnsignedFloat, SignedInteger, Join
from lepl.matchers.combine import Or
from lepl.matchers.core import Any
from lepl._test.base import BaseTest


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, R0201, R0913, R0901, R0904
# (dude this is just a test)

#basicConfig(level=DEBUG)


class FloatTest(BaseTest):
    
    def test_first(self):
        self.assert_direct('1.e3', Join(UnsignedFloat(), Any('eE'), SignedInteger()),
                           [['1.e3']])
    
    def test_second(self):
        self.assert_direct('1.e3', UnsignedFloat(), [['1.']])
        
    def test_all(self):
        first = Join(UnsignedFloat(), Any('eE'), SignedInteger())
        second = UnsignedFloat()
        all = Or(first, second)
        all.config.default() # wrong order
        #all.config.compile_to_dfa() # gives 1.e3 only
        #all.config.compile_to_nfa() # wrong order
        #all.config.no_compile_to_regexp() # ok
        #all.config.clear() # ok
        self.assert_direct('1.e3', all, [['1.e3'], ['1.']])
    
    def test_nfa(self):
        first = Join(UnsignedFloat(), Any('eE'), SignedInteger())
        second = UnsignedFloat()
        all = Or(first, second)
        all.config.clear().compile_to_nfa()
        m = all.get_parse()
        #print(m.matcher)
        #print(m.matcher.regexp)
        
# (?:
#  (?:
#   (?:[0-9]
#    (?:[0-9])*
#   )?
#   \.[0-9](?:[0-9])*
#  |
#   [0-9](?:[0-9])*(?:\.)?
#  )
#  [Ee](?:[\+\-])?[0-9](?:[0-9])*
# |
#  (?:
#   (?:
#    [0-9](?:[0-9])*
#   )?\.[0-9](?:[0-9])*
#  |
#   [0-9](?:[0-9])*\.
#  )
# )
#DEBUG:lepl.regexp.core.Compiler:compiling to nfa: (?P<label>(?:(?:(?:[0-9](?:[0-9])*)?\.[0-9](?:[0-9])*|[0-9](?:[0-9])*(?:\.)?)[Ee](?:[\+\-])?[0-9](?:[0-9])*|(?:[0-9](?:[0-9])*)?\.[0-9](?:[0-9])*|[0-9](?:[0-9])*\.))
#DEBUG:lepl.regexp.core.Compiler:nfa graph: 0: [0-9]->5, 10, 4, 18; 1; 2(label): 1; 3: [Ee]->14; 4: \.->7; 5: 6; 6: [0-9]->6, 4; 7: [0-9]->8; 8: 9; 9: [0-9]->9, 3; 10: [0-9]->12; 11: \.->3, 3; 12: 13; 13: [0-9]->13, 11; 14: [\+\-]->15, 15; 15: [0-9]->16; 16: 17; 17: [0-9]->17, 2; 18: [0-9]->20, 25, 19; 19: \.->22; 20: 21; 21: [0-9]->21, 19; 22: [0-9]->23; 23: 24; 24: [0-9]->24, 2; 25: [0-9]->27; 26: \.->2; 27: 28; 28: [0-9]->28, 26
# 0: [0-9]->5, 10, 4, 18; 
# 1; 
# 2(label): 1; 
# 3: [Ee]->14; 
# 4: \.->7; 
# 5: 6; 
# 6: [0-9]->6, 4; 
# 7: [0-9]->8; 
# 8: 9; 
# 9: [0-9]->9, 3; 
# 10: [0-9]->12; 
# 11: \.->3, 3; 
# 12: 13; 
# 13: [0-9]->13, 11; 
# 14: [\+\-]->15, 15; 
# 15: [0-9]->16; 
# 16: 17; 
# 17: [0-9]->17, 2; 
# 18: [0-9]->20, 25, 19; 
# 19: \.->22; 
# 20: 21; 
# 21: [0-9]->21, 19; 
# 22: [0-9]->23; 
# 23: 24; 
# 24: [0-9]->24, 2; 
# 25: [0-9]->27; 
# 26: \.->2; 
# 27: 28; 
# 28: [0-9]->28, 26
