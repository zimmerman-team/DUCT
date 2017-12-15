
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
Initial, minimal support for dynamic variables.  This allows you to use a
value found in matching as part of another matcher IN SOME RESTRICTED CASES.
'''

from unittest import TestCase

from lepl import Apply, UnsignedInteger, Repeat, Any
from lepl.core.dynamic import IntVar


class DynamicTest(TestCase):

    def test_lt(self):
        three = IntVar(3)
        assert three < 4
        assert 2 < three
        assert 3 == three

    def test_dynamic(self):
        size = IntVar()
        header = Apply(UnsignedInteger(), size.setter())
        body = Repeat(Any(), stop=size, add_=True)
        matcher = ~header & body
        matcher.config.no_compile_to_regexp().no_full_first_match()
        result = next(matcher.match_string("3abcd"))[0]
        assert result == ['abc'], result
