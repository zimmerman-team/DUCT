from lepl.support._test.node import NodeTest
from lepl.core.rewriters import NodeStats, NodeStats2

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
Example returning less results than before.
'''

from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *

class CacheTest(TestCase):
    
    def test_cache(self):
        #basicConfig(level=DEBUG)
        
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
    
        group3c.config.clear().lexer().auto_memoize().trace_variables()
        p = group3c.get_parse_all()
        #print(p.matcher.tree())
        results = list(p('1+2*(3-4)+5/6+7'))
        for result in results:
            #print(result[0])
            pass
        assert len(results) == 12, results

    def test_left(self):
        #basicConfig(level=DEBUG)
        a = Delayed()
        a += Optional(a) & (a | 'b' | 'c')
        for (conservative, full, d, n) in [(None, True, 0, 104),
                                           (None, True, 1, 38),
                                           (False, False, 1, 38)]:
            a.config.clear().no_full_first_match().auto_memoize(
                        conservative=conservative, full=full, d=d)
            p = a.get_parse_all()
            #print(p.matcher.tree())
            r = list(p('bcb'))
            assert len(r) == n, (n, len(r), r)
            
    def test_trace_variables(self):
        # for comparison
        with TraceVariables():
            a = Delayed()
            a += Optional(a) & (a | 'b' | 'c')

        #print('\n*** clear')
        a.config.clear().no_full_first_match()
        p = a.get_parse_all()
        #print(p.matcher.tree())
        #print(NodeStats2(p.matcher))

        #print('*** trace_variables')
        a.config.clear().no_full_first_match().trace_variables()
        p = a.get_parse_all()
        #print(p.matcher.tree())
        #print(NodeStats2(p.matcher))

        #print('*** auto_memoize')
        a.config.clear().no_full_first_match().auto_memoize()
        p = a.get_parse_all()
        #print(p.matcher.tree())
        #print(NodeStats2(p.matcher))
        r = list(p('bcb'))
        assert len(r) == 104, (len(r), r)

        #basicConfig(level=DEBUG)
        a.config.clear().no_full_first_match().auto_memoize().trace_variables()
        p = a.get_parse_all()
        #print('*** trace_variables and memoize')
        #print(p.matcher.tree())
        #print(NodeStats2(p.matcher))
        r = list(p('bcb'))
        assert len(r) == 104, (len(r), r)
        