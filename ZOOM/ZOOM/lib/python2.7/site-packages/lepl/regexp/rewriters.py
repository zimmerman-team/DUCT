
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
Rewrite the tree of matchers from the bottom up (as far as possible)
using regular expressions.  This is complicated by a number of things.

First, intermediate parts of regular expressions are not matchers, so we need 
to keep them inside a special container type that we can detect and convert to
a regular expression when needed (since at some point we cannot continue with
regular expressions).

Second, we sometimes do not know if our regular expression can be used until we 
have moved higher up the matcher tree.  For example, And() might convert all
sub-expressions to a sequence if it's parent is an Apply(add).  So we may
need to store several alternatives, along with a way of selecting the correct
alternative.

So cloning a node may give either a matcher or a container.  The container
will provide both a matcher and an intermediate regular expression.  The logic
for handling odd dependencies is more difficult to implement in a general
way, because it is not clear what all cases may be.  For now, therefore,
we use a simple state machine approach using a tag (which is almost always
None).  
'''

from logging import getLogger
from operator import __add__

from lepl.matchers.core import Regexp
from lepl.matchers.matcher import Matcher, matcher_map
from lepl.matchers.support import FunctionWrapper, SequenceWrapper, \
    TrampolineWrapper, TransformableTrampolineWrapper
from lepl.regexp.core import Choice, Sequence, Repeat, Empty, Option
from lepl.regexp.matchers import NfaRegexp, DfaRegexp
from lepl.regexp.interval import Character
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.core.rewriters import clone, Rewriter, clone_matcher
from lepl.support.lib import fmt, str, basestring
from lepl.matchers.combine import DepthNoTrampoline, AndNoTrampoline
from lepl.matchers.error import Error


class RegexpContainer(object):
    '''
    The container referred to above, which carries a regular expression and
    an alternative matcher "up the tree" during rewriting.
    '''
    
    log = getLogger('lepl.regexp.rewriters.RegexpContainer')

    def __init__(self, matcher, regexp, use, add_reqd=False):
        self.matcher = matcher   # current best matcher (regexp or not)
        self.regexp = regexp     # the current regexp
        self.use = use           # is the regexp a win?
        self.add_reqd = add_reqd # we need "add" to combine values (from And)?
        
    def __str__(self):
        return ','.join([str(self.matcher.__class__), str(self.regexp), 
                         str(self.use), str(self.add_reqd)])

    @classmethod
    def to_regexps(cls, use, possibles, have_add=False):
        '''
        Convert to regular expressions.
        
        `have_add` indicaes whether the caller can supply an "add".
        None - caller doesn't care what lower code needed.
        True - caller has add, and caller should need that.
        False - caller doesn't have add, and caller should not need it.
        '''
        regexps = []
        for possible in possibles:
            if isinstance(possible, RegexpContainer):
                cls.log.debug(fmt('unpacking: {0!s}', possible))
                if have_add is None or possible.add_reqd == have_add:
                    regexps.append(possible.regexp)
                    # this flag indicates that it's "worth" using the regexp
                    # so we "inherit"
                    use = use or possible.use
                else:
                    raise Unsuitable('Add inconsistent.')
            else:
                cls.log.debug(fmt('cannot unpack: {0!s}', 
                                     possible.__class__))
                raise Unsuitable('Not a container.')
        return (use, regexps)
        
    @staticmethod
    def to_matcher(possible):
        '''
        Convert to a matcher.
        '''
        if isinstance(possible, RegexpContainer):
            return possible.matcher
        else:
            return possible
        
    @classmethod
    def build(cls, node, regexp, alphabet, regexp_type, use, 
               add_reqd=False, wrapper=None):
        '''
        Construct a container or matcher.
        '''
        if use and not add_reqd:
            matcher = single(alphabet, node, regexp, regexp_type, wrapper)
            # if matcher is a Transformable with a Transformation other than
            # the standard empty_adapter then we must stop
            if len(matcher.wrapper.functions) > 1:
                cls.log.debug(fmt('Force matcher: {0}', matcher.wrapper))
                return matcher
        else:
            # not good enough to have a regexp as default, so either force
            # the original matcher if it has transforms, or keep going in the
            # hope we can get more complex later
            matcher = node
            if hasattr(matcher, 'wrapper') and matcher.wrapper:
                return matcher
        return RegexpContainer(matcher, regexp, use, add_reqd)
        

def single(alphabet, node, regexp, regexp_type, wrapper=None):
    '''
    Create a matcher for the given regular expression.
    '''
    # avoid dependency loops
    from lepl.matchers.transform import TransformationWrapper
    matcher = regexp_type(regexp, alphabet)
    matcher = matcher.compose(TransformationWrapper(empty_adapter))
    if wrapper is None and hasattr(node, 'wrapper'):
        wrapper = node.wrapper
    elif wrapper and not isinstance(wrapper, TransformationWrapper):
        wrapper = TransformationWrapper(wrapper)
    if wrapper:
        wrapper.functions = \
                list(filter(lambda x: x != empty_adapter, wrapper.functions))
        matcher = matcher.compose(wrapper)
    return matcher

def empty_adapter(_stream, matcher):
    '''
    There is a fundamental mismatch between regular expressions and the 
    recursive descent parser on how empty matchers are handled.  The main 
    parser uses empty lists; regexp uses an empty string.  This is a hack
    that converts from one to the other.  I do not see a better solution.
    '''
    (results, stream_out) = matcher()
    if results == ['']:
        results = []
    return (results, stream_out)

        
class Unsuitable(Exception):
    '''
    Exception thrown when a sub-node does not contain a suitable matcher.
    '''
    pass


def make_clone(alphabet_, old_clone, regexp_type, use_from_start):
    '''
    Factory that generates a clone suitable for rewriting recursive descent
    to regular expressions.
    '''
    
    # clone functions below take the "standard" clone and the node, and then
    # reproduce the normal argument list of the matcher being cloned.
    # they should return either a container or a matcher.
    
    # Avoid dependency loops
    from lepl.matchers.derived import add
    from lepl.matchers.combine import And, Or, DepthFirst
    from lepl.matchers.core import Any, Literal
    from lepl.matchers.transform import Transform

    log = getLogger('lepl.regexp.rewriters.make_clone')
    
    def clone_any(use, original, restrict=None):
        '''
        We can always convert Any() to a regular expression; the only question
        is whether we have an open range or not.
        '''
        if restrict is None:
            char = Character([(alphabet_.min, alphabet_.max)], alphabet_)
        else:
            char = Character(((char, char) for char in restrict), alphabet_)
        log.debug(fmt('Any: cloned {0}', char))
        regexp = Sequence(alphabet_, char)
        return RegexpContainer.build(original, regexp, alphabet_, 
                                     regexp_type, use)
        
    def clone_or(use, original, *matchers):
        '''
        We can convert an Or only if all the sub-matchers have possible
        regular expressions.
        '''
        (use, regexps) = \
            RegexpContainer.to_regexps(use, matchers, have_add=False)
        regexp = Choice(alphabet_, *regexps)
        log.debug(fmt('Or: cloned {0}', regexp))
        return RegexpContainer.build(original, regexp, alphabet_, 
                                     regexp_type, use)

    def clone_and(use, original, *matchers):
        '''
        We can convert an And only if all the sub-matchers have possible
        regular expressions, and even then we must tag the result unless
        an add transform is present.
        '''
        if hasattr(original, 'wrapper'):
            wrapper = original.wrapper.functions
        else:
            wrapper = None
        add_reqd = True
        if wrapper:
            if wrapper[0] is add:
                wrapper = wrapper[1:]
                add_reqd = False
            else:
                raise Unsuitable
        try:
            # combine all
            (use, regexps) = \
                RegexpContainer.to_regexps(use, matchers, have_add=None)
            # if we have regexp sub-expressions, join them
            regexp = Sequence(alphabet_, *regexps)
            log.debug(fmt('And: cloning {0}', regexp))
            return RegexpContainer.build(original, regexp, alphabet_, 
                                         regexp_type, use, add_reqd=add_reqd,
                                         wrapper=wrapper)
        except Unsuitable:
            # combine contiguous matchers where possible
            if add_reqd:
                raise
            def unpack(matcher):
                original = RegexpContainer.to_matcher(matcher)
                try:
                    return (original, 
                            RegexpContainer.to_regexps(use, [matcher], 
                                                       have_add=None)[1][0])
                except Unsuitable:
                    return (original, None)
            output = []
            (regexps, originals) = ([], [])
            for (matcher, regexp) in [unpack(matcher) for matcher in matchers]:
                if regexp:
                    regexps.append(regexp)
                    originals.append(matcher)
                else:
                    if len(regexps) > 1:
                        # combine regexps
                        output.append(
                            regexp_type(Sequence(alphabet_, *regexps), 
                                         alphabet_))
                    else:
                        output.extend(originals)
                    output.append(matcher)
                    (regexps, originals) = ([], [])
            if len(regexps) > 1:
                output.append(
                    regexp_type(Sequence(alphabet_, *regexps), alphabet_))
            else:
                output.extend(originals)
            merged = And(*output)
            return merged.compose(original.wrapper)
        
    def clone_transform(use, original, matcher, wrapper):
        '''
        We can assume that wrapper is a transformation.  Add joins into
        a sequence.
        '''
        if original.wrapper:
            if original.wrapper.functions[0] is add:
                have_add = True
                wrapper = original.wrapper.functions[1:]
            else:
                have_add = False
                wrapper = original.wrapper.functions
        else:
            # punt to next level
            return matcher
        (use, [regexp]) = \
            RegexpContainer.to_regexps(use, [matcher], have_add=have_add)
        log.debug(fmt('Transform: cloning {0}', regexp))
        return RegexpContainer.build(original, regexp, alphabet_, 
                                     regexp_type, use,
                                     add_reqd=False, wrapper=wrapper)
        
    def clone_literal(use, original, text):
        '''
        Literal values are easy to transform.
        '''
        chars = [Character([(c, c)], alphabet_) for c in text]
        regexp = Sequence(alphabet_, *chars)
        log.debug(fmt('Literal: cloned {0}', regexp))
        return RegexpContainer.build(original, regexp, alphabet_, 
                                     regexp_type, use)
    
    def clone_regexp(use, original, pattern, alphabet=None):
        '''
        Regexps values are also easy.
        '''
        try:
            if isinstance(pattern, basestring):
                pattern = Sequence(alphabet_, *alphabet_.parse(pattern))
        except TypeError:
            raise Unsuitable
        except Error: # cannot parse regexp
            raise Unsuitable
        return RegexpContainer.build(original, pattern, alphabet_, 
                                     regexp_type, use)
    
    def clone_dfs(use, original, first, start, stop, rest=None, reduce=None, 
                  generator_manager_queue_len=None):
        '''
        This forces use=True as it is likely that a regexp is a gain.
        '''
        if stop is not None and start > stop:
            raise Unsuitable
        if reduce and not (isinstance(reduce, tuple) 
                           and len(reduce) == 2
                           and reduce[0] == [] 
                           and reduce[1] == __add__):
            raise Unsuitable
        if generator_manager_queue_len:
            # this should only be set when running
            raise Unsuitable
        add_reqd = stop is None or stop > 1
        wrapper = False
        if hasattr(original, 'wrapper') and original.wrapper:
            if original.wrapper.functions[0] is add:
                add_reqd = False
                wrapper = original.wrapper.functions[1:]
            else:
                raise Unsuitable
        rest = first if rest is None else rest
        (use, [first, rest]) = \
                RegexpContainer.to_regexps(True, [first, rest], have_add=None)
        seq = []
        if first != rest:
            seq.append(first.clone())
        while len(seq) < start:
            seq.append(rest.clone())
        addzero = len(seq) > start # first was exceptional and start=0
        if stop:
            if stop > start:
                # use nested form to avoid inefficient nfa
                extras = Option(alphabet_, rest.clone())
                for _i in range(stop - start - 1):
                    extras = Option(alphabet_, 
                                    Sequence(alphabet_, rest.clone(), extras))
                seq.append(extras)
        else:
            seq.append(Repeat(alphabet_, rest.clone()))
        regexp = Sequence(alphabet_, *seq)
        if addzero:
            regexp = Choice(alphabet_, regexp, Empty(alphabet_))
        log.debug(fmt('DFS: cloned {0}', regexp))
        return RegexpContainer.build(original, regexp, alphabet_, 
                                     regexp_type, use, add_reqd=add_reqd,
                                     wrapper=wrapper)
        
    def clone_wrapper(use, original, *args, **kargs):
        factory = original.factory
        if factory in map_:
            log.debug(fmt('Found {0}', factory))
            return map_[factory](use, original, *args, **kargs)
        else:
            log.debug(fmt('No clone for {0}, {1}', factory, map_.keys()))
            return original
        
    map_ = matcher_map({Any: clone_any, 
                        Or: clone_or, 
                        And: clone_and,
                        AndNoTrampoline: clone_and,
                        Transform: clone_transform,
                        Literal: clone_literal,
                        Regexp: clone_regexp,
                        NfaRegexp: clone_regexp,
                        DfaRegexp: clone_regexp,
                        DepthFirst: clone_dfs,
                        DepthNoTrampoline: clone_dfs,
                        FunctionWrapper: clone_wrapper,
                        SequenceWrapper: clone_wrapper,
                        TrampolineWrapper: clone_wrapper,
                        TransformableTrampolineWrapper: clone_wrapper})
    
    def clone_(i, j, node, args, kargs):
        '''
        Do the cloning, dispatching by type to the methods above.
        '''
        original_args = [RegexpContainer.to_matcher(arg) for arg in args]
        original_kargs = dict((name, RegexpContainer.to_matcher(kargs[name]))
                              for name in kargs)
        original = old_clone(i, j, node, original_args, original_kargs)
        type_ = type(node)
        if type_ in map_:
            # pylint: disable-msg=W0142
            try:
                return map_[type_](use_from_start, original, *args, **kargs)
            except Unsuitable:
                pass
        return original

    return clone_


class CompileRegexp(Rewriter):
    '''
    A rewriter that uses the given alphabet and matcher to compile simple
    matchers.
    
    The "use" parameter controls when regular expressions are substituted.
    If true, they are always used.  If false, they are used only if they
    are part of a tree that includes repetition.  The latter case generally
    gives more efficient parsers because it avoids converting already
    efficient literal matchers to regular expressions.
    '''
    
    def __init__(self, alphabet=None, use=True, matcher=NfaRegexp):
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        super(CompileRegexp, self).__init__(Rewriter.COMPILE_REGEXP,
            fmt('CompileRegexp({0}, {1}, {2})', alphabet, use, matcher))
        self.alphabet = alphabet
        self.use = use
        self.matcher = matcher
        
    def __call__(self, graph):
        new_clone = make_clone(self.alphabet, clone, self.matcher, self.use)
        graph = clone_matcher(graph, new_clone)
        graph = RegexpContainer.to_matcher(graph)
        return graph 
