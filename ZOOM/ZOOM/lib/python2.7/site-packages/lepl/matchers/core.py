
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
Matchers that embody fundamental, common actions.
'''

# pylint: disable-msg=C0103,W0212
# (consistent interfaces)
# pylint: disable-msg=E1101
# (_args create attributes)
# pylint: disable-msg=R0901, R0904, W0142
# lepl conventions

from re import compile as compile_

from lepl.stream.core import s_next, s_eq, s_empty, s_line
from lepl.core.parser import tagged
from lepl.matchers.support import OperatorMatcher, coerce_, \
    function_matcher, function_matcher_factory, trampoline_matcher_factory, \
    to, sequence_matcher
from lepl.support.lib import fmt


@sequence_matcher
def Never(support, stream):
    '''
    Always fails to match.
    
    (in this package rather than lepl.matchers.memo to simplify import 
    dependencies)
    '''
    if False:
        yield


@function_matcher_factory()
def Any(restrict=None):
    '''
    Create a matcher for a single character.
    
    :Parameters:
    
      restrict (optional)
        A list of tokens (or a string of suitable characters).  
        If omitted any single token is accepted.  
        
        **Note:** This argument is *not* a sub-matcher.
    '''
    warned = [False]

    def match(support, stream):
        '''
        Do the matching.  The result will be a single matching character.
        '''
        (value, next_stream) = s_next(stream)
        if restrict:
            try:
                if value not in restrict:
                    raise StopIteration
            except TypeError:
                # it would be nice to make this an error, but for line aware
                # parsing (and any other heterogenous input) it's legal
                if not warned[0]:
                    support._warn(fmt('Cannot restrict {0} with {1!r}',
                                          value, restrict))
                    warned[0] = True
                    raise StopIteration
        return ([value], next_stream)
            
    return match
            
            
@function_matcher_factory()
def Literal(text):
    '''
    Match a series of tokens in the stream (**''**).

    Typically the argument is a string but a list might be appropriate 
    with some streams.
    '''
    delta = len(text)
    def match(support, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).

        Need to be careful here to use only the restricted functionality
        provided by the stream interface.
        '''
        try:
            (value, next_stream) = s_next(stream, count=delta)
            if text == value:
                return ([value], next_stream)
        except IndexError:
            pass
    return match

       
@function_matcher
def Empty(support, stream):
    '''
    Match any stream, consumes no input, and returns nothing.
    '''
    return ([], stream)
 

class Lookahead(OperatorMatcher):
    '''
    Tests to see if the embedded matcher *could* match, but does not do the
    matching.  On success an empty list (ie no result) and the original
    stream are returned.
    
    When negated (preceded by ~) the behaviour is reversed - success occurs
    only if the embedded matcher would fail to match.
    
    This is a consumer because it's correct functioning depends directly on
    the stream's contents.
    '''
    
    def __init__(self, matcher, negated=False):
        '''
        On success, no input is consumed.
        If negated, this will succeed if the matcher fails.  If the matcher is
        a string it is coerced to a literal match.
        '''
        super(Lookahead, self).__init__()
        self._arg(matcher=coerce_(matcher))
        self._karg(negated=negated)
    
    @tagged
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).
        '''
        try:
            yield self.matcher._match(stream) # an evaluation, not a return
            success = True
        except StopIteration:
            success = False
        if success is self.negated:
            return
        else:
            yield ([], stream)
            
    def __invert__(self):
        '''
        Invert the semantics (this overrides the usual meaning for ~).
        '''
        return Lookahead(self.matcher, negated=not self.negated)
            

@function_matcher_factory()
def Regexp(pattern):
    '''
    Match a regular expression.  If groups are defined, they are returned
    as results.  Otherwise, the entire expression is returned.

    If the pattern contains groups, they are returned as separate results,
    otherwise the whole match is returned.
    
    :Parameters:
    
      pattern
        The regular expression to match. 
    '''
    pattern = compile_(pattern)
    
    def match(support, stream):
        (line, _) = s_line(stream, True)
        match = pattern.match(line)
        if match:
            eaten = len(match.group())
            if match.groups():
                return (list(match.groups()), s_next(stream, count=eaten)[1])
            else:
                return ([match.group()], s_next(stream, count=eaten)[1])
    return match
        

class Delayed(OperatorMatcher):
    '''
    A placeholder that allows forward references (**+=**).  Before use a 
    matcher must be assigned via '+='.
    '''
    
    def __init__(self, matcher=None):
        '''
        Introduce the matcher.  It can be defined later with '+='
        '''
        super(Delayed, self).__init__()
        self._karg(matcher=matcher)
        if matcher:
            self._match = matcher._match
            
    def assert_matcher(self):
        if not self.matcher:
            raise ValueError('Delayed matcher still unbound.')
            
    def _match(self, stream):
        '''
        Do the matching (return a generator that provides successive 
        (result, stream) tuples).  This is overwritten when a matcher is
        defined.
        '''
        self.assert_matcher()
        
    # pylint: disable-msg=E0203, W0201
    # _karg defined this in constructor
    def __iadd__(self, matcher):
        if self.matcher:
            raise ValueError('Delayed matcher already bound.')
        else:
            self.matcher = coerce_(matcher)
            self._match = matcher._match
            return self
        

@function_matcher
def Eof(support, stream):
    '''
    Match the end of a stream.  Returns nothing.  

    This is also aliased to Eos in lepl.derived.
    '''
    if s_empty(stream):
        return ([], stream)


@trampoline_matcher_factory(matcher=to(Literal))
def Consumer(matcher, consume=True):
    '''
    Only accept the match if it consumes data from the input
    '''
    def match(support, stream_in):
        '''
        Do the match and test whether the stream has progressed.
        '''
        try:
            generator = matcher._match(stream_in)
            while True:
                (result, stream_out) = yield generator
                if consume != s_eq(stream_in, stream_out):
                    yield (result, stream_out)
        except StopIteration:
            pass
    return match


