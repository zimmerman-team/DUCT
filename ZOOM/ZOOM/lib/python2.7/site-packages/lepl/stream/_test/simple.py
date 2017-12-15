
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


from lepl.support.lib import fmt
from lepl._test.base import BaseTest
from lepl.stream.core import s_empty, s_fmt, s_line, s_next, s_stream
from lepl.stream.factory import DEFAULT_STREAM_FACTORY


class GenericTest(BaseTest):
    
    def test_empty(self):
        f = DEFAULT_STREAM_FACTORY
        for (constructor, data) in ((f.from_sequence, ''), 
                                    (f.from_sequence, []),
                                    (f.from_sequence, ()),
                                    (f.from_string, ''),
                                    (f.from_list, [])):
            s = constructor(data)
            assert s_empty(s)
            try:
                s_next(s)
                assert False, fmt('expected error: {0}', s) 
            except StopIteration:
                pass
            try:
                s_line(s, False)
                assert False, fmt('expected error: {0}', s) 
            except StopIteration:
                pass
        
    def test_single_value(self):
        f = DEFAULT_STREAM_FACTORY
        for (constructor, data) in ((f.from_sequence, 'a'), 
                                    (f.from_sequence, [1]),
                                    (f.from_sequence, (2,)),
                                    (f.from_string, 'b'),
                                    (f.from_list, ['c'])):
            s = constructor(data)
            assert not s_empty(s)
            (value, n) = s_next(s)
            assert value == data
            assert s_empty(n)
            (line, n) = s_line(s, False)
            assert line == data
            assert s_empty(n)
            
    def test_two_values(self):
        f = DEFAULT_STREAM_FACTORY
        for (constructor, data) in ((f.from_sequence, 'ab'), 
                                    (f.from_sequence, [1, 2]),
                                    (f.from_sequence, (2,3)),
                                    (f.from_string, 'bc'),
                                    (f.from_list, ['c', 6])):
            s = constructor(data)
            assert not s_empty(s)
            (value, n) = s_next(s)
            assert value == data[0:1]
            (value, n) = s_next(n)
            assert value == data[1:2]
            assert s_empty(n)
            (line, n) = s_line(s, False)
            assert line == data
            assert s_empty(n)

    def test_string_lines(self):
        f = DEFAULT_STREAM_FACTORY
        s = f.from_string('line 1\nline 2\nline 3\n')
        (l, s) = s_line(s, False)
        assert l == 'line 1\n', l
        (l, _) = s_line(s, False)
        assert l == 'line 2\n', repr(l)
        locn = s_fmt(s, '{location}')
        assert locn == 'line 2, character 1', locn
        sl = s_stream(s, l)
        (_, sl) = s_next(sl, count=2)
        locn = s_fmt(sl, '{location}')
        assert locn == 'line 2, character 3', locn
        
        
        