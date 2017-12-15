
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
A regexp implementation for unicode strings.
'''

from sys import maxunicode

from lepl.regexp.str import StrAlphabet, ILLEGAL
from lepl.support.lib import chr, lmap, fmt

_WHITESPACE = '\u0009\u000A\u000B\u000C\u000D\u0020\u0085\u00A0\u1680' \
                '\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007' \
                '\u2008\u2009\u200a\u2028\u2029\u202F\u205F\u3000'
'''http://en.wikipedia.org/wiki/Whitespace_character'''


class UnicodeAlphabet(StrAlphabet):
    '''
    An alphabet for unicode strings.
    '''
    
    __cached_instance = None
    
    # pylint: disable-msg=E1002
    # (pylint bug?  this chains back to a new style abc)
    def __init__(self):
        from lepl.matchers.core import Any
        from lepl.matchers.combine import Or
        max_ = chr(maxunicode)
        def mkhex(char, n):
            from lepl.matchers.derived import Drop
            return Drop(Any(char)) + Any('0123456789abcdefABCDEF')[n,...] >> \
                        (lambda x: chr(int(x, 16)))
        def mkchr(char, range, invert=False):
            from lepl.matchers.core import Literal
            from lepl.matchers.derived import Map
            from lepl.regexp.core import Character
            intervals = lmap(lambda x: (x, x), range)
            if invert:
                # this delays call to invert until after creation of self
                func = lambda _: Character(self.invert(intervals), self)
            else:
                func = lambda _: Character(intervals, self)
            return Map(Literal(char), func)
        range = Or(mkchr('s', _WHITESPACE),
                   mkchr('S', _WHITESPACE, invert=True))
        escaped = Any(ILLEGAL) | mkhex('x', 2) | mkhex('u', 4) | mkhex('U', 8)
        super(UnicodeAlphabet, self).__init__(chr(0), max_, escaped=escaped,
                                              range=range)
        
    def before(self, char):
        '''
        Must return the character before char in the alphabet.  Never called 
        with min (assuming input data are in range).
        ''' 
        return chr(ord(char)-1)
    
    def after(self, char): 
        '''
        Must return the character after c in the alphabet.  Never called with
        max (assuming input data are in range).
        ''' 
        return chr(ord(char)+1)
    
    @classmethod
    def instance(cls):
        '''
        Get an instance of this alphabet (avoids creating new objects).
        '''
        if cls.__cached_instance is None:
            cls.__cached_instance = UnicodeAlphabet()
        return cls.__cached_instance

    def __repr__(self):
        return '<Unicode>'

