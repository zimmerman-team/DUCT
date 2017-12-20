
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

from lepl.lexer.matchers import Token, RestrictTokensBy, EmptyToken
from lepl.lexer.lines.lexer import START, END
from lepl.lexer.lines.monitor import BlockMonitor
from lepl.matchers.support import coerce_, OperatorMatcher, NoMemo
from lepl.core.parser import tagged
from lepl.support.lib import fmt
from lepl.matchers.combine import And
from lepl.stream.core import s_key, s_next, s_line


NO_BLOCKS = object()
'''
Magic initial value for block_offset to disable indentation checks.
'''


class LineStart(Token):
        
    def __init__(self, indent=True, regexp=None, content=None, id_=None, 
                 alphabet=None, complete=True, compiled=False):
        '''
        Arguments used only to support cloning.
        '''
        super(LineStart, self).__init__(regexp=None, content=None, id_=START, 
                                        alphabet=None, complete=True, 
                                        compiled=compiled)
        self._karg(indent=indent)
        self.monitor_class = BlockMonitor
        self._current_indent = NO_BLOCKS
        
    def on_push(self, monitor):
        '''
        Read the global indentation level.
        '''
        if self.indent:
            self._current_indent = monitor.indent
        
    def on_pop(self, monitor):
        '''
        Unused
        '''
    
    @tagged
    def _match(self, stream_in):
        '''
        Check that we match the current level
        '''
        try:
            generator = super(LineStart, self)._match(stream_in)
            while True:
                (indent, stream) = yield generator
                self._debug(fmt('SOL {0!r}', indent))
                if indent and indent[0] and indent[0][-1] == '\n': 
                    indent[0] = indent[0][:-1]
                # if we're not doing indents, this is empty
                if not self.indent:
                    yield ([], stream)
                # if we are doing indents, we need a match or NO_BLOCKS
                elif self._current_indent == NO_BLOCKS or \
                        len(indent[0]) == self._current_indent:
                    yield (indent, stream)
                else:
                    self._debug(
                        fmt('Incorrect indent ({0:d} != len({1!r}), {2:d})',
                               self._current_indent, indent[0], 
                               len(indent[0])))
        except StopIteration:
            pass


class LineEnd(EmptyToken):
    
    def __init__(self, regexp=None, content=None, id_=None, alphabet=None,
                  complete=True, compiled=False):
        '''
        Arguments used only to support cloning.
        '''
        super(LineEnd, self).__init__(regexp=None, content=None, id_=END, 
                                      alphabet=None, complete=True, 
                                      compiled=compiled)


def Line(matcher, indent=True):
    '''
    Match the matcher within a line.
    '''
    return ~LineStart(indent=indent) & matcher & ~LineEnd()


def ContinuedLineFactory(matcher):
    '''
    Create a replacement for ``Line()`` that can match multiple lines if they
    end in the given character/matcher.
    '''
    matcher = coerce_(matcher, lambda regexp: Token(regexp))
    restricted = RestrictTokensBy(matcher, LineEnd(), LineStart())
    def factory(matcher, indent=True):
        return restricted(Line(matcher, indent=indent))
    return factory


def Extend(matcher):
    '''
    Apply the given matcher to a token stream that ignores line endings and
    starts (so it matches over multiple lines).
    '''
    start = LineStart()
    end = LineEnd()
    return RestrictTokensBy(end, start)(matcher)


# pylint: disable-msg=W0105
# epydoc convention
DEFAULT_TABSIZE = 8
'''
The default number of spaces for a tab.
'''

def constant_indent(n_spaces):
    '''
    Construct a simple policy for `Block` that increments the indent
    by some fixed number of spaces.
    '''
    def policy(current, _indent):
        '''
        Increment current by n_spaces
        '''
        return current + n_spaces
    return policy


def explicit(_current, indent):
    '''
    Another simple policy that matches whatever indent is used.
    '''
    return len(indent)


def to_right(current, indent):
    '''
    This allows new blocks to be used without any introduction (eg no colon
    on the preceding line).  See the "closed_bug" test for more details.
    '''
    new = len(indent)
    if new <= current:
        raise StopIteration
    return new


DEFAULT_POLICY = constant_indent(DEFAULT_TABSIZE)
'''
By default, expect an indent equivalent to a tab.
'''

# pylint: disable-msg=E1101, W0212, R0901, R0904
# pylint conventions
class Block(OperatorMatcher, NoMemo):
    '''
    Set a new indent level for the enclosed matchers (typically `BLine` and
    `Block` instances).
    
    In the simplest case, this might increment the global indent by 4, say.
    In a more complex case it might look at the current token, expecting an
    `Indent`, and set the global indent at that amount if it is larger
    than the current value.
    
    A block will always match an `Indent`, but will not consume it
    (it will remain in the stream after the block has finished).
    
    The usual memoization of left recursive calls will not detect problems
    with nested blocks (because the indentation changes), so instead we
    track and block nested calls manually.
    '''
    
    POLICY = 'policy'
    
# Python 2.6 does not support this syntax
#    def __init__(self, *lines, policy=None, indent=None):
    def __init__(self, *lines, **kargs):
        '''
        Lines are invoked in sequence (like `And()`).
        
        The policy is passed the current level and the indent and must 
        return a new level.  Typically it is set globally by rewriting with
        a default in the configuration.  If it is given as an integer then
        `constant_indent` is used to create a policy from that.
        
        indent is the matcher used to match indents, and is exposed for 
        rewriting/extension (in other words, ignore it).
        '''
        super(Block, self).__init__()
        self._args(lines=lines)
        policy = kargs.get(self.POLICY, DEFAULT_POLICY)
        if isinstance(policy, int):
            policy = constant_indent(policy)
        self._karg(policy=policy)
        self.monitor_class = BlockMonitor
        self.__monitor = None
        self.__streams = set()
        
    def on_push(self, monitor):
        '''
        Store a reference to the monitor which we will update inside _match
        '''
        self.__monitor = monitor
        
    def on_pop(self, monitor):
        pass
        
    @tagged
    def _match(self, stream_in):
        '''
        Pull indent and call the policy and update the global value, 
        then evaluate the contents.
        '''
        # detect a nested call
        key = s_key(stream_in)
        if key in self.__streams:
            self._debug('Avoided left recursive call to Block.')
            return
        self.__streams.add(key)
        try:
            ((tokens, token_stream), _) = s_next(stream_in)
            (indent, _) = s_line(token_stream, True)
            if START not in tokens:
                raise StopIteration
            current = self.__monitor.indent
            policy = self.policy(current, indent)
            
            generator = And(*self.lines)._match(stream_in)
            while True:
                self.__monitor.push_level(policy)
                try:
                    results = yield generator
                finally:
                    self.__monitor.pop_level()
                yield results
        finally:
            self.__streams.remove(key)
