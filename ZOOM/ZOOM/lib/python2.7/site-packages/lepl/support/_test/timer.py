
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
Tests for the lepl.support.timer module.
'''

from unittest import TestCase

from lepl import *
from lepl.support.lib import StringIO


class TimerTest(TestCase):
    
    def test_luca(self):
        '''
        See mailing list.
        '''
        integer = Token(Integer()) >> int 
        uletter = Token(Upper()) 
        real = Token(Real()) >> float 
        data_line = Line(integer & uletter & real[6]) 
        table = data_line[1:] 
        
        source = '''1      G      0.0            0.0 0.0            0.0            0.0            0.0 
2      G      0.0            0.0 0.0            0.0            0.0            0.0 
3      G      0.0            0.0 0.0            0.0            0.0            0.0 
4      G      0.0            0.0 0.0            0.0            0.0            0.0 
5      G      0.0            0.0 0.0            0.0            0.0            0.0 
6      G      0.0            0.0 0.0            0.0            0.0            0.0 
7      G      0.0            0.0 0.0            0.0            0.0            0.0 
8      G      0.0            0.0 0.0            0.0            0.0            0.0 
9      G      0.0            0.0           -9.856000E-05 -1.444699E-17   1.944000E-03   0.0 
10      G      0.0            0.0           -9.856000E-05 -1.427843E-17   1.944000E-03   0.0 
11      G      0.0            0.0           -1.085216E-02 -2.749537E-16   1.874400E-02   0.0 
12      G      0.0            0.0           -1.085216E-02 -2.748317E-16   1.874400E-02   0.0 
13      G      0.0            0.0           -3.600576E-02 -6.652665E-16   3.074400E-02   0.0 
14      G      0.0            0.0           -3.600576E-02 -6.717988E-16   3.074400E-02   0.0 
15      G      0.0            0.0           -7.075936E-02 -8.592844E-16   3.794400E-02   0.0 
16      G      0.0            0.0           -7.075936E-02 -8.537008E-16   3.794400E-02   0.0 
17      G      0.0            0.0           -1.103130E-01 -9.445027E-16   4.034400E-02   0.0 
18      G      0.0            0.0           -1.103130E-01 -9.538811E-16   4.034400E-02   0.0 
100      G      0.0            0.0 0.0            0.0            0.0            0.0 
200      G      0.0            0.0 0.0            0.0            0.0            0.0 
''' 

        out = StringIO()
        print_timing(source, 
            {'Real()': table.clone().config.lines().matcher,
             'Real() no memoize': table.clone().config.lines().no_memoize().matcher},
             count_compile=1, out=out)
        table = out.getvalue()
        print(table)
        assert 'Timing Results' in table, table
        
