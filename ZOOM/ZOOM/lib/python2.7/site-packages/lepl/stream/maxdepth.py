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
Raise an exception if the stream is not consumed entirely.
'''

from lepl.stream.core import s_empty, s_fmt, s_deepest, s_next
from lepl.matchers.support import trampoline_matcher_factory


@trampoline_matcher_factory()
def FullFirstMatch(matcher, eos=True):
    '''
    Raise an exception if the first match fails (if eos=False) or does not
    consume the entire input stream (eos=True).  The exception includes 
    information about the location of the deepest match.
    
    This only works for the first match because we cannot reset the stream
    facade for subsequent matches (also, if you want multiple matches you
    probably want more sophisticated error handling than this).
    '''
    
    def _matcher(support, stream1):
        # set default maxdepth
        s_next(stream1, count=0)
        # first match
        generator = matcher._match(stream1)
        try:
            (result2, stream2) = yield generator
            if eos and not s_empty(stream2):
                raise FullFirstMatchException(stream2)
            else:
                yield (result2, stream2)
        except StopIteration:
            raise FullFirstMatchException(stream1)
        
        # subsequent matches:
        while True:
            result = yield generator
            yield result

    return _matcher


class FullFirstMatchException(Exception):
    '''
    The exception raised by `FullFirstMatch`.  This includes information
    about the deepest point read in the stream. 
    '''
    
    def __init__(self, stream):
        super(FullFirstMatchException, self).__init__(
            s_fmt(s_deepest(stream),
                     'The match failed in {filename} at {rest} ({location}).'))

