
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


from lepl._test.base import BaseTest
from lepl.stream.core import s_empty, s_fmt, s_line, s_next, s_stream, \
    s_debug, s_deepest
from lepl.stream.factory import DEFAULT_STREAM_FACTORY


class GenericTest(BaseTest):
    
    def test_all(self):
        lines = iter(['first line', 'second line', 'third line'])
        f = DEFAULT_STREAM_FACTORY
        s1 = f(lines)
        # just created
        assert not s_empty(s1)
        # get first line
        (l1, s2) = s_line(s1, False)
        assert 'first line' == l1, l1
        # get first character of next line
        (c21, s21) = s_next(s2)
        assert c21 == 's', c21
        # and test fmtting
        locn = s_fmt(s21, '{location}: {rest}')
        assert locn == "line 2, character 2: 'econd line'", locn
        # then get rest of second line
        (c22, s3) = s_next(s21, count=len('econd line'))
        assert c22 == 'econd line', c22
        d = s_debug(s21)
        assert d == "1:'e'", d
        # and move on to third line
        (c31, s31) = s_next(s3)
        assert c31 == 't', c31
        (c32, s32) = s_next(s31)
        assert c32 == 'h', c32
        # now try branching (think tokens) at line 1
        s10 = s_stream(s2, l1)
        (l1, s20) = s_line(s10, False)
        assert l1 == 'first line', l1
        assert not s_empty(s20)
        (c1, s11) = s_next(s10)
        assert c1 == 'f', c1
        d = s_debug(s11)
        assert d == "1:'i'", d
        # finally look at max depth (which was after 'h' in third line)
        m = s_deepest(s1)
        locn = s_fmt(m, '{location}: {rest}')
        assert locn == "line 3, character 3: 'ird line'", locn
        
        