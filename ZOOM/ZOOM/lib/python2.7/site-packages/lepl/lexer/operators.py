
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
Operators for tokens.
'''


from lepl.support.context import Namespace
from lepl.matchers.operators import ADD, AND, OR, APPLY, APPLY_RAW, NOT, \
    KARGS, RAISE, REPEAT, FIRST, MAP, RepeatWrapper, REDUCE
from lepl.matchers.derived import Add, Apply, Drop, KApply, Map
from lepl.matchers.combine import And, Or, First
from lepl.matchers.error import raise_error


TOKENS = 'tokens'
'''
This names a per-thread storage area that contains the definitions of 
operators (so tokens can have different operators to non-tokens).  All
token matchers should reference this (either directly via `NamespaceMixin`
or indirectly via `BaseToken`).
'''


class TokenNamespace(Namespace):
    '''
    A modified version of the usual ``OperatorNamespace`` without handling of
    spaces (since that is handled by the lexer), allowing Tokens and other
    matchers to be configured separately (because they process different 
    types).
    
    At one point this also defined alphabet and discard, used by the rewriter,
    but because those are global values it makes more sense to supply them
    directly to the rewriter.
    '''
    
    def __init__(self):
        super(TokenNamespace, self).__init__({
            ADD:       lambda a, b: Add(And(a, b)),
            AND:       And,
            OR:        Or,
            APPLY:     Apply,
            APPLY_RAW: lambda a, b: Apply(a, b, raw=True),
            NOT:       Drop,
            KARGS:     KApply,
            RAISE:     lambda a, b: KApply(a, raise_error(b)),
            REPEAT:    RepeatWrapper,
            FIRST:     First,
            MAP:       Map,
            REDUCE:    None,
        })
        


