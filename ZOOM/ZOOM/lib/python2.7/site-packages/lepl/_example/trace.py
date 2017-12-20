
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,W0621,W0703
# (the code style is for documentation, not "real")

'''
Examples from the documentation.

(The WithVariables() example is covered in a test for config)
'''


from logging import basicConfig, INFO, DEBUG

from lepl import *
from lepl._example.support import Example
from lepl.support.lib import StringIO


class NodeErrorTest(Example):
    
    def test_deepest(self):

        buffer = StringIO()
        # this test fails when run in a batch because logs are configured 
        # differently beforehand!
        basicConfig(level=INFO, stream=buffer)
#        basicConfig(level=INFO)
        
        name    = Word()              > 'name'
        phone   = Integer()           > 'phone'
        line    = name / ',' / phone  > make_dict
        matcher = line[0:,~Newline()]
        matcher.config.clear().record_deepest()
        matcher.parse('andrew, 3333253\n bob, 12345')
        
        trace = buffer.getvalue()
        assert trace == r"""INFO:lepl.core.trace._RecordDeepest:
Up to 6 matches before and including longest match:
00105 '3333253\n' 8/1.9 (0008) 006 (['3333253'], (15, <helper>))  ->  Transform(And, TransformationWrapper(<add>))(8:'3')  ->  (['3333253'], (15, <helper>))
00106 '3333253\n' 8/1.9 (0008) 005 (['3333253'], (15, <helper>))  ->  Transform(Transform, TransformationWrapper(<apply>))(8:'3')  ->  ([('phone', '3333253')], (15, <helper>))
00107 'andrew...' 0/1.1 (0000) 004 ([('phone', '3333253')], (15, <helper>))  ->  And(And, Transform, Transform)(0:'a')  ->  ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], (15, <helper>))
00108 'andrew...' 0/1.1 (0000) 003 ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], (15, <helper>))  ->  Transform(And, TransformationWrapper(<apply>))(0:'a')  ->  ([{'phone': '3333253', 'name': 'andrew'}], (15, <helper>))
00113 '\n'        15/1.16 (0015) 004 next(Literal('\n')(15:'\n'))  ->  (['\n'], (16, <helper>))
00114 '\n'        15/1.16 (0015) 005 (['\n'], (16, <helper>))  ->  Or(Literal, Literal)(15:'\n')  ->  (['\n'], (16, <helper>))
Up to 2 failures following longest match:
00123 ' bob, ...' 16/2.1 (0016) 008 next(NfaRegexp('[^ \t\n\r\x0b\x0c]', <Unicode>)(16:' '))  ->  stop
00124 ' bob, ...' 16/2.1 (0016) 009 stop  ->  And(NfaRegexp, DepthFirst)(16:' ')  ->  stop
Up to 2 successful matches following longest match:
00139 'andrew...' 0/1.1 (0000) 002 stop  ->  DepthFirst(None, None, ([], <built-in function __add__>), rest=And, 0, first=Transform)(0:'a')  ->  ([{'phone': '3333253', 'name': 'andrew'}], (15, <helper>))

""", 'r"""'+trace+'"""'


