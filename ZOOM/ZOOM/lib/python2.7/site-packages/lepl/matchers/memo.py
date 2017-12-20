
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
Memoisation (both as described by Norvig 1991, giving Packrat 
parsers for non-left recursive grammars, and the equivalent described by
Frost and Hafiz 2006 which allows left-recursive grammars to be used).
 
Note that neither paper describes the extension to backtracking with
generators implemented here. 
'''

from itertools import count

from lepl.matchers.core import OperatorMatcher
from lepl.matchers.matcher import is_child
from lepl.matchers.support import NoMemo
from lepl.core.parser import tagged
from lepl.stream.core import s_key, s_len
from lepl.support.state import State


# pylint: disable-msg=R0901, R0904
# lepl conventions


class MemoException(Exception):
    '''
    Exception raised for problems with memoisation.
    '''
    
def RMemo(matcher):
    '''
    Wrap in the _RMemo cache if required.
    '''
    if is_child(matcher, NoMemo, fail=False):
        return matcher
    else:
        return _RMemo(matcher)


class _RMemo(OperatorMatcher):
    '''
    A simple memoizer for grammars that do not have left recursion.
    
    Making this class Transformable did not improve performance (it's better
    to place the transformation on critical classes like Or and And). 
    '''
    
    # pylint: disable-msg=E1101
    # (using _args to define attributes)
    
    def __init__(self, matcher):
        super(_RMemo, self).__init__()
        self._arg(matcher=matcher)
        self.__table = {} # s_key(stream) -> [lock, table, generator] 
        self.__state = State.singleton()
    
    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        key = s_key(stream, self.__state)
        if key not in self.__table:
            self.__table[key] = [False, [], self.matcher._match(stream)]
        descriptor = self.__table[key]
        if descriptor[0]:
            raise MemoException('''Left recursion was detected.
You can try .config.auto_memoize() or similar, but it is better to re-write 
the parser to remove left-recursive definitions.''')
        for i in count():
            assert not descriptor[0]
            if i == len(descriptor[1]):
                try:
                    descriptor[0] = True
                    result = yield descriptor[2]
                finally:
                    descriptor[0] = False
                descriptor[1].append(result)
            yield descriptor[1][i]
                    
    def _untagged_match(self, stream):
        '''
        Match the stream without trampolining.
        '''
        key = s_key(stream, self.__state)
        if key not in self.__table:
            self.__table[key] = [False, [], self.matcher._match(stream)]
        descriptor = self.__table[key]
        if descriptor[0]:
            raise MemoException('''Left recursion was detected.
You can try .config.auto_memoize() or similar, but it is better to re-write 
the parser to remove left-recursive definitions.''')
        for i in count():
            assert not descriptor[0]
            if i == len(descriptor[1]):
                result = next(descriptor[2].generator)
                descriptor[1].append(result)
            yield descriptor[1][i]
            
    def __iadd__(self, other):
        '''
        Allow memos to wrap Delayed in rewriting.
        '''
        self.matcher += other
        return self


def LMemo(matcher, curtail=None):
    '''
    Wrap in the _LMemo cache if required.
    '''
    if is_child(matcher, NoMemo, fail=False):
        return matcher
    else:
        if curtail is None:
            curtail = lambda depth, length: depth > length
        return _LMemo(matcher, curtail)


class _LMemo(OperatorMatcher):
    
    def __init__(self, matcher, curtail):
        super(_LMemo, self).__init__()
        self._arg(matcher=matcher)
        self._karg(curtail=curtail)
        self.__depth = {} # s_key(stream) -> [depth] 
        self.__table = {} # (s_key(stream), depth) -> [table, generator] 
        self.__state = State.singleton()
    
    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        key = s_key(stream, self.__state)
        if key not in self.__depth:
            self.__depth[key] = 0
        depth = self.__depth[key]
        if self.curtail(depth, s_len(stream)):
            return
        if (key, depth) not in self.__table:
            self.__table[(key, depth)] = [[], self.matcher._match(stream)]
        descriptor = self.__table[(key, depth)]
        for i in count():
            assert depth == self.__depth[key]
            if i == len(descriptor[0]):
                try:
                    self.__depth[key] += 1
                    result = yield descriptor[1]
                finally:
                    self.__depth[key] -= 1
                descriptor[0].append(result)
            yield descriptor[0][i]
                    
    def _untagged_match(self, stream):
        '''
        Match the stream without trampolining.
        '''
        key = s_key(stream, self.__state)
        if key not in self.__depth:
            self.__depth[key] = 0
        depth = self.__depth[key]
        if self.curtail(depth, s_len(stream)):
            return
        if (key, depth) not in self.__table:
            self.__table[(key, depth)] = [[], self.matcher._match(stream)]
        descriptor = self.__table[(key, depth)]
        for i in count():
            assert depth == self.__depth[key]
            if i == len(descriptor[0]):
                result = next(descriptor[1].generator)
                descriptor[0].append(result)
            yield descriptor[0][i]

    def __iadd__(self, other):
        '''
        Allow memos to wrap Delayed in rewriting.
        '''
        self.matcher += other
        return self
