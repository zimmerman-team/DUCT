
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
Complex matchers that are rearely used.
'''

from lepl.matchers.core import Literal
from lepl.regexp.matchers import DfaRegexp
from lepl.matchers.support import to, trampoline_matcher_factory
from lepl.stream.factory import DEFAULT_STREAM_FACTORY
from lepl.stream.core import s_line, s_stream, s_next, s_fmt, s_id
from lepl.support.lib import fmt


@trampoline_matcher_factory(matcher=to(Literal), condition=to(DfaRegexp))
def PostMatch(matcher, condition, not_=False, equals=True, stream_factory=None):
    '''
    Apply the condition to each result from the matcher.  It should return
    either an exact match (equals=True) or simply not fail (equals=False).
    If `not_` is set, the test is inverted.
    
    `matcher` is coerced to `Literal()`, condition to `DfaRegexp()`
    
    `factory` is used to generate a stream from the result.  If not set the
    default factory is used.
    '''
    def match(support, stream_in, stream_factory=stream_factory):
        '''
        Do the match and test the result.
        '''
        stream_factory = stream_factory if stream_factory else DEFAULT_STREAM_FACTORY
        generator = matcher._match(stream_in)
        while True:
            (results, stream_out) = yield generator
            success = True
            for result in results:
                if not success: break
                generator2 = condition._match(stream_factory(result))
                try:
                    (results2, _ignored) = yield generator2
                    if not_:
                        # if equals is false, we need to fail just because
                        # we matched.  otherwise, we need to fail only if
                        # we match.
                        if not equals or (len(results2) == 1 or 
                                          results2[0] == result):
                            success = False
                    else:
                        # if equals is false, not generating an error is
                        # sufficient, otherwise we must fail if the result
                        # does not match
                        if equals and (len(results2) != 1 or 
                                       results2[0] != result):
                            success = False
                except:
                    # fail unless if we were expecting any kind of match
                    if not not_:
                        success = False
            if success:
                yield (results, stream_out)
    
    return match


@trampoline_matcher_factory()
def _Columns(indices, *matchers):

    def match(support, stream):
        # we increment id so that different strings (which might overlap or
        # be contiguous) don't affect each other's memoisation (the hash key
        # is based on offset and ('one past the') end of one column can have
        # the same offset as the start of the next).
        id_ = s_id(stream)
        # extract a line
        (line, next_stream) = s_line(stream, False)
        line_stream = s_stream(stream, line)
        results = []
        for ((left, right), matcher) in zip(indices, matchers):
            id_ += 1
            # extract the location in the line
            (_, left_aligned_line_stream) = s_next(line_stream, count=left)
            (word, _) = s_next(left_aligned_line_stream, count=right-left)
            support._debug(fmt('Columns {0}-{1} {2!r}', left, right, word))
            word_stream = s_stream(left_aligned_line_stream, word, id_=id_)
            # do the match
            support._debug(s_fmt(word_stream, 'matching {rest}'))
            (result, _) = yield matcher._match(word_stream)
            results.extend(result)
        support._debug(repr(results))
        yield (results, next_stream)
        
    return match
    
    
def Columns(*columns, **kargs):
    '''
    Match data in a set of columns.
    
    This is a fairly complex matcher.  It allows matchers to be associated 
    with a range of indices (measured from the current point in the stream)
    and only succeeds if all matchers succeed.  The results are returned in
    a list, in the same order as the matchers are specified.
    
    A range if indices is given as a tuple (start, stop) which works like an
    array index.  So (0, 4) selects the first four characters (like [0:4]).
    Alternatively, a number of characters can be given, in which case they
    start where the previous column finished (or at zero for the first).
    
    The matcher for each column will see the (selected) input data as a 
    separate stream.  If a matcher should consume the entire column then
    it should check for `Eos`.
    
    Finally, the skip parameter controls how data to "the right" of the
    columns is handled.  If unset, the data are discarded (this functions
    as an additional, final, column that currently drops data).  Data to
    "the left" are simply discarded.
    
    Note: This does not support backtracking over the columns.
    '''
    # Note - this is the public-facing wrapper that pre-process the arguments  
    # so that matchers are handled correctly during cloning.  The work is done 
    # by `_Columns`.
    def clean():
        right = 0
        for (col, matcher) in columns:
            try:
                (left, right) = col
            except TypeError:
                left = right
                right = right + col
            yield ((left, right), matcher)
    (indices, matchers) = zip(*clean())
    return _Columns(indices, *matchers)


@trampoline_matcher_factory()
def Iterate(matcher):
    '''
    This isn't complex to implement, but conceptually is rather odd.  It takes
    a single matcher and returns a result for each match as it consumes the
    input.
    
    This means `parse_all()` is needed to retrieve the entire result (and there
    is no backtracking).
    
    In practice this means that if you have a matcher whose top level is a
    repeating element (for example, lines in a file) then you can treat the 
    entire parser as a lazy iterator over the input.   The obvious application
    is with `.config.low_memory()` as this allows for large output to be 
    generated without consuming a large amount of memory.
    '''
    def match(support, stream):
        while True:
            (result, stream) = yield matcher._match(stream)
            yield (result, stream)
    return match
