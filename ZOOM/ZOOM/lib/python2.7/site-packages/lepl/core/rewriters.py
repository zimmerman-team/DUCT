
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
Rewriters modify the graph of matchers before it is used to generate a 
parser.
'''

from lepl.matchers.memo import LMemo, RMemo
from lepl.support.graph import Visitor, preorder, loops, order, NONTREE, \
    dfs_edges, LEAF
from lepl.matchers.combine import DepthFirst, DepthNoTrampoline, \
    BreadthFirst, BreadthNoTrampoline, And, AndNoTrampoline, \
    Or, OrNoTrampoline
from lepl.matchers.core import Delayed, Lookahead
from lepl.matchers.derived import add
from lepl.matchers.matcher import Matcher, is_child, FactoryMatcher, \
    matcher_type, MatcherTypeException, canonical_matcher_type
from lepl.matchers.support import NoTrampoline, Transformable
from lepl.support.lib import lmap, fmt, LogMixin, empty, count


class Rewriter(LogMixin):
    '''
    base class for rewriters, supporting a fixed ordering.
    '''
    
    # ordering
    (SET_ARGUMENTS,
     COMPOSE_TRANSFORMS,
     FLATTEN,
     COMPILE_REGEXP,
     OPTIMIZE_OR,
     LEXER,
     DIRECT_EVALUATION,
     # memoize must come before anything that wraps a delayed node.  this is
     # because the left-recursive memoizer uses delayed() instances as markers
     # for where to duplicate state for different paths through the call
     # graph; if these are wrapped or replaced then the assumptions made there
     # fail (and left-recursive parsers fail to match).
     MEMOIZE,
     TRACE_VARIABLES,
     FULL_FIRST_MATCH) = range(10, 110, 10)
       
    def __init__(self, order_, name=None, exclusive=True):
        super(Rewriter, self).__init__()
        self.order = order_
        self.name = name if name else self.__class__.__name__
        self.exclusive = exclusive
        
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.exclusive or self is other
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        if self.exclusive:
            return hash(self.__class__)
        else:
            return super(Rewriter, self).__hash__()
        
    def __lt__(self, other):
        if not isinstance(other, Rewriter):
            return True
        elif self.exclusive or self.order != other.order:
            return self.order < other.order
        else:
            return hash(self) < hash(other)
            
    def __ge__(self, other):
        return not self.__lt__(other)
    
    def __gt__(self, other):
        if not isinstance(other, Rewriter):
            return True
        elif self.exclusive or self.order != other.order:
            return self.order > other.order
        else:
            return hash(self) > hash(other)

    def __le__(self, other):
        return not self.__gt__(other)
    
    def __call__(self, matcher):
        return matcher
    
    def __str__(self):
        return self.name
    

def clone(i, j, node, args, kargs):
    '''
    Clone a single node, including matcher-specific attributes.
    '''
    from lepl.support.graph import clone as old_clone
    copy = old_clone(node, args, kargs)
    copy_standard_attributes(node, copy)
    return copy


def copy_standard_attributes(node, copy):
    '''
    Handle the additional attributes that matchers may have.
    '''
    if isinstance(node, Transformable):
        copy.wrapper = node.wrapper
    if isinstance(node, FactoryMatcher):
        copy.factory = node.factory
    if hasattr(node, 'trace_variables'):
        copy.trace_variables = node.trace_variables


def linearise_matcher(node):
    '''
    Return `[(head, reversed), ...]` where each tuple describes  a tree of 
    matchers without loops.  The first head is the root node.  The reversed
    list contains nodes ordered children-first (except for `Delayed()`
    instances, whose children are other `head` elements). 
    
    This allows us to clone a DAG of matchers in the same way as it was first
    created - by creating linear trees and then connecting the `Delayed()`
    instances.
    
    The postorder ordering is used to match the ordering in the more general
    iteration over matchers based on the graph support classes and helps
    keep things consistent (there was a strange issue where the `.tree()`
    display of a cloned graph differed from the original that, I think, was
    due to a different ordering).
    '''
    linear = []
    pending = [node]
    heads = set()
    while pending:
        node = pending.pop()
        if node not in heads:
            stack = []
            def append(child):
                if isinstance(child, Matcher):
                    if isinstance(child, Delayed):
                        child.assert_matcher()
                        pending.append(child.matcher)
                        stack.append((child, empty()))
                    else:
                        stack.append((child, iter(child)))
            heads.add(node)
            append(node) # init stack
            def postorder():
                while stack:
                    (node, children) = stack[-1]
                    try:
                        append(next(children))
                    except StopIteration:
                        yield stack.pop()[0]
            linear.append((node, list(postorder())))
    return linear


def clone_tree(i, head, reversed, mapping, delayed, clone, duplicate=False):
    '''
    Clone a tree of matchers.  This clones all the matchers in a linearised
    set, except for the `Delayed()` instances, which are re-created without
    their contents (these are set later, to connect the trees into the 
    final matcher DAG).
    
    `i` is the index of the tree (0 for the first tree, which cannot be part
    of a loop itself).  It is passed to the clone function.
    
    `head` is the root of the tree.
    
    `reversed` are the tree nodes in postorder
    
    `mapping` is a map from old to new node of all the nodes created.  For 
    `Delayed()` instances, if `duplicate=True`, then the new node is just
    one of possibly many copies.
    
    `clone` is the function used to create a new node instance.
    
    `duplicate` controls how `Delayed()` instances are handled.  If true then
    a new instance is created for each one.  This does not preserve the 
    graph, but is used by memoisation.
    '''
    def rewrite(value):
        try:
            if value in mapping:
                return mapping[value]
        except TypeError:
            pass
        return value
    n = len(reversed)
    for (j, node) in zip(count(n, -1), reversed):
        if isinstance(node, Delayed):
            if duplicate or node not in mapping:
                mapping[node] = clone(i, -j, node, (), {})
                delayed.append((node, mapping[node]))
        else:
            if node not in mapping:
                (args, kargs) = node._constructor_args()
                args = lmap(rewrite, args)
                kargs = dict((name, rewrite(value)) for (name, value) in kargs.items())
                copy = clone(i, j, node, args, kargs)
                mapping[node] = copy


def clone_matcher(node, clone=clone, duplicate=False):
    '''
    This used to be implemented using the graph support classes 
    (`ConstructorWalker()` etc).  But the left-recursive handling was
    unreliable and that was too opaque to debug easily.  It's possible this
    code could now be moved back to that approach, as not everything
    here is used (the `j` index turned out not to be useful, for example).
    But this approach is easier to understand and I am not 100% sure that
    the code is correct, so I may need to continue working on this.
    
    `node` is the root of the matcher graph.
    
    `clone` is a function used to create new instances.
    
    `duplicate` controls how `Delayed()` instances are handled.  If true then
    a new instance is created for each one.  This does not preserve the 
    graph, but is used by memoisation.
    '''
    from lepl.regexp.rewriters import RegexpContainer
    trees = linearise_matcher(node)
    all_nodes = {}
    all_delayed = []
    for (i, (head, reversed)) in enumerate(trees):
        clone_tree(i, head, reversed, all_nodes, all_delayed, clone, 
                   duplicate=duplicate)
    for (delayed, clone) in all_delayed:
        # this lets us delay forcing to matcher until last moment
        # we had bugs where this ended up being delegated to +
        clone.__iadd__(RegexpContainer.to_matcher(all_nodes[delayed.matcher]))
    return RegexpContainer.to_matcher(all_nodes[node])
        
    
def post_clone(function):
    '''
    Generate a clone function that applies the given function to the newly
    constructed node, except for Delayed instances (which are effectively
    proxies and so have no functionality of their own) (so, when used with 
    `DelayedClone`, effectively performs a map on the graph).
    '''
    def new_clone(i, j, node, args, kargs):
        '''
        Apply function as well as clone.
        '''
        copy = clone(i, j, node, args, kargs)
        # ignore Delayed since that would (1) effectively duplicate the
        # action and (2) they come and go with each cloning.
        if not isinstance(node, Delayed):
            copy = function(copy)
        return copy
    return new_clone


class Flatten(Rewriter):
    '''
    A rewriter that flattens `And` and `Or` lists.
    '''
    
    def __init__(self):
        super(Flatten, self).__init__(Rewriter.FLATTEN)
    
    def __call__(self, graph):
        def new_clone(i, j, node, old_args, kargs):
            '''
            The flattening cloner.
            '''
            new_args = []
            type_ = matcher_type(node, fail=False)
            if type_ in map(canonical_matcher_type, [And, Or]):
                for arg in old_args:
                    if matcher_type(arg, fail=False) is type_ and \
                        (not hasattr(arg, 'wrapper') or
                         ((not arg.wrapper and not node.wrapper) or \
                          (arg.wrapper.functions == node.wrapper.functions 
                           and node.wrapper.functions == [add]))):
                        new_args.extend(arg.matchers)
                    else:
                        new_args.append(arg)
            if not new_args:
                new_args = old_args
            return clone(i, j, node, new_args, kargs)
        return clone_matcher(graph, new_clone)
   

class ComposeTransforms(Rewriter):
    '''
    A rewriter that joins adjacent transformations into a single
    operation, avoiding trampolining in some cases.
    '''

    def __init__(self):
        super(ComposeTransforms, self).__init__(Rewriter.COMPOSE_TRANSFORMS)
        
    def __call__(self, graph):
        from lepl.matchers.transform import Transform, Transformable
        def new_clone(i, j, node, args, kargs):
            '''
            The joining cloner.
            '''
            # must always clone to expose the matcher (which was cloned 
            # earlier - it is not node.matcher)
            copy = clone(i, j, node, args, kargs)
            if isinstance(copy, Transform) \
                    and isinstance(copy.matcher, Transformable):
                return copy.matcher.compose(copy.wrapper)
            else:
                return copy
        return clone_matcher(graph, new_clone)


class TraceVariables(Rewriter):
    '''
    A rewriter needed for TraceVariables which adds the trace_variables
    attribute to untransformable matchers that need a transform.
    '''

    def __init__(self):
        super(TraceVariables, self).__init__(Rewriter.TRACE_VARIABLES)
        
    def __call__(self, graph):
        from lepl.matchers.transform import Transform
        def new_clone(i, j, node, args, kargs):
            '''
            The joining cloner.
            '''
            # must always clone to expose the matcher (which was cloned 
            # earlier - it is not node.matcher)
            copy = clone(i, j, node, args, kargs)
            if hasattr(node, 'trace_variables') and node.trace_variables:
                return Transform(copy, node.trace_variables)
            else:
                return copy
        return clone_matcher(graph, new_clone)


class RightMemoize(Rewriter):
    '''
    A rewriter that adds RMemo to all nodes in the matcher graph.
    '''
    
    def __init__(self):
        super(RightMemoize, self).__init__(Rewriter.MEMOIZE, 'Right memoize')
        
    def __call__(self, graph):
        return clone_matcher(graph, post_clone(RMemo))

    
class LeftMemoize(Rewriter):
    '''
    A rewriter that adds LMemo to all nodes in the matcher graph.
    '''
    
    def __init__(self, d=0):
        super(LeftMemoize, self).__init__(Rewriter.MEMOIZE, 'Left memoize')
        self.d = d
        
    def __call__(self, graph):
        def new_clone(i, j, node, args, kargs):
            copy = clone(i, j, node, args, kargs)
            return self.memoize(i, j, self.d, copy, LMemo)
        return clone_matcher(graph, new_clone, duplicate=True)
    
    @staticmethod
    def memoize(i, j, d, copy, memo):
        if j > 0:
            def open(depth, length):
                return False
            curtail = open
        elif d:
            def fixed(depth, length):
                return depth >  i * d
            curtail = fixed
        else:
            def slen(depth, length):
                return depth > i * length
            curtail = slen
        return memo(copy, curtail)


class AutoMemoize(Rewriter):
    '''
    Apply two different memoizers, one to left recursive loops and the
    other elsewhere (either can be omitted).
    
    `conservative` refers to the algorithm used to detect loops:
      `None` will use the left memoizer on all nodes except the initial tree
      `True` will detect all possible loops (should be very similar to `None`)
      `False` detects only left-most loops and may miss some loops.
      
    `d` is a parameter that controls the depth to which repeated left-recursion
    may occur.  If `None` then the length of the remaining input is used.
    If set, parsers are more efficient, but less likely to match input
    correctly.
    '''
    
    def __init__(self, conservative=None, left=None, right=None, d=0):
        super(AutoMemoize, self).__init__(Rewriter.MEMOIZE,
            fmt('AutoMemoize({0}, {1}, {2})', conservative, left, right))
        self.conservative = conservative
        self.left = left
        self.right = right
        self.d = d

    def __call__(self, graph):
        dangerous = set()
        for head in order(graph, NONTREE, Matcher):
            for loop in either_loops(head, self.conservative):
                for node in loop:
                    dangerous.add(node)
        def new_clone(i, j, node, args, kargs):
            '''
            Clone with the appropriate memoizer 
            (cannot use post_clone as need to test original)
            '''
            copy = clone(i, j, node, args, kargs)
            if (self.conservative is None and i) or node in dangerous:
                if self.left:
                    return LeftMemoize.memoize(i, j, self.d, copy, self.left)
                else:
                    return copy
            else:
                if self.right:
                    return self.right(copy)
                else:
                    return copy
        return clone_matcher(graph, new_clone, duplicate=True)


def left_loops(node):
    '''
    Return (an estimate of) all left-recursive loops from the given node.
    
    We cannot know for certain whether a loop is left recursive because we
    don't know exactly which parsers will consume data.  But we can estimate
    by assuming that all matchers eventually (ie via their children) consume
    something.  We can also improve that slightly by ignoring `Lookahead`.
    
    So we estimate left-recursive loops as paths that start and end at
    the given node, and which are first children of intermediate nodes
    unless the node is `Or`, or the preceding matcher is a
    `Lookahead`.  
    
    Each loop is a list that starts and ends with the given node.
    '''
    stack = [[node]]
    known = set([node]) # avoid getting lost in embedded loops
    while stack:
        ancestors = stack.pop()
        parent = ancestors[-1]
        if isinstance(parent, Matcher):
            for child in parent:
                family = list(ancestors) + [child]
                if child is node:
                    yield family
                else:
                    try:
                        if child not in known:
                            stack.append(family)
                            known.add(child)
                    # random attribute that is list, etc
                    except TypeError:
                        pass
                if not is_child(parent, Or, fail=False) and \
                        not is_child(child, Lookahead, fail=False):
                    break
    
                    
def either_loops(node, conservative):
    '''
    Select between the conservative and liberal loop detection algorithms.
    '''
    if conservative:
        return loops(node, Matcher)
    else:
        return left_loops(node)
    

class OptimizeOr(Rewriter):
    '''
    A rewriter that re-arranges `Or` matcher contents for left--recursive 
    loops.
    
    When a left-recursive rule is used, it is much more efficient if it
    appears last in an `Or` statement, since that forces the alternates
    (which correspond to the terminating case in a recursive function)
    to be tested before the LMemo limit is reached.
    
    This rewriting may change the order in which different results for
    an ambiguous grammar are returned.
    
    `conservative` refers to the algorithm used to detect loops; False
    may classify some left--recursive loops as right--recursive.
    '''
    
    def __init__(self, conservative=True):
        super(OptimizeOr, self).__init__(Rewriter.OPTIMIZE_OR)
        self.conservative = conservative

    def __call__(self, graph):
        self._warn('Alternatives are being re-ordered to improve stability with left-recursion.\n'
                   'This will change the ordering of results.')
        #raise Exception('wtf')
        for delayed in [x for x in preorder(graph, Matcher) 
                        if isinstance(x, Delayed)]:
            for loop in either_loops(delayed, self.conservative):
                for i in range(len(loop)):
                    if is_child(loop[i], Or, fail=False):
                        # we cannot be at the end of the list here, since that
                        # is a Delayed instance
                        # copy from tuple to list
                        loop[i].matchers = list(loop[i].matchers)
                        matchers = loop[i].matchers
                        target = loop[i+1]
                        # move target to end of list
                        index = matchers.index(target)
                        del matchers[index]
                        matchers.append(target)
        return graph


class SetArguments(Rewriter):
    '''
    Add/replace named arguments while cloning.
    
    This rewriter is not exclusive - several different instances canb be
    defined in parallel.
    '''
    
    def __init__(self, type_, **extra_kargs):
        super(SetArguments, self).__init__(Rewriter.SET_ARGUMENTS,
            fmt('SetArguments({0}, {1})', type_, extra_kargs), False)
        self.type = type_
        self.extra_kargs = extra_kargs
        
    def __call__(self, graph):
        def new_clone(i, j, node, args, kargs):
            '''
            As clone, but add in any extra kargs if the node is an instance
            of the given type.
            '''
            if isinstance(node, self.type):
                for key in self.extra_kargs:
                    kargs[key] = self.extra_kargs[key]
            return clone(i, j, node, args, kargs)
        return clone_matcher(graph, new_clone)


class DirectEvaluation(Rewriter):
    '''
    Replace given matchers if all Matcher arguments are subclasses of
    `NoTrampolineWrapper`
    
    `spec` is a map from original matcher type to the replacement.
    '''
    
    def __init__(self, spec=None):
        super(DirectEvaluation, self).__init__(Rewriter.DIRECT_EVALUATION,
            fmt('DirectEvaluation({0})', spec))
        if spec is None:
            spec = {DepthFirst: DepthNoTrampoline,
                    BreadthFirst: BreadthNoTrampoline,
                    And: AndNoTrampoline,
                    Or: OrNoTrampoline}
        self.spec = spec

    def __call__(self, graph):
        def new_clone(i, j, node, args, kargs):
            type_, ok = None, False
            for parent in self.spec:
                if is_child(node, parent):
                    type_ = self.spec[parent]
            if type_:
                ok = True
                for arg in args:
                    if isinstance(arg, Matcher) and not \
                            isinstance(arg, NoTrampoline):
                        ok = False
                for name in kargs:
                    arg = kargs[name]
                    if isinstance(arg, Matcher) and not \
                            isinstance(arg, NoTrampoline):
                        ok = False
            if not ok:
                type_ = type(node)
            try:
                copy = type_(*args, **kargs)
                copy_standard_attributes(node, copy)
                return copy
            except TypeError as err:
                raise TypeError(fmt('Error cloning {0} with ({1}, {2}): {3}',
                                       type_, args, kargs, err))
        return clone_matcher(graph, new_clone)
    
    
class FullFirstMatch(Rewriter):
    '''
    If the parser fails, raise an error at the maxiumum depth.
    
    `eos` controls whether or not the entire input must be consumed for the
    parse to be considered a success. 
    '''
    
    def __init__(self, eos=False):
        super(FullFirstMatch, self).__init__(Rewriter.FULL_FIRST_MATCH,
                                       fmt('FullFirstMatch({0})', eos))
        self.eos = eos
        
    def __call__(self, graph):
        from lepl.stream.maxdepth import FullFirstMatch
        return FullFirstMatch(graph, self.eos)


class NodeStats(object):
    '''
    Provide statistics and access by type to nodes.
    '''
    
    def __init__(self, matcher=None):
        self.loops = 0
        self.leaves = 0
        self.total = 0
        self.others = 0
        self.duplicates = 0
        self.unhashable = 0
        self.types = {}
        self.__known = set()
        if matcher is not None:
            self.add_all(matcher)
        
    def add(self, type_, node):
        '''
        Add a node of a given type.
        '''
        try:
            node_type = matcher_type(node)
        except MatcherTypeException:
            node_type = type(node)
        if type_ & LEAF:
            self.leaves += 1
        if type_ & NONTREE and is_child(node_type, Matcher, fail=False):
            self.loops += 1
        try:
            if node not in self.__known:
                self.__known.add(node)
                if node_type not in self.types:
                    self.types[node_type] = set()
                self.types[node_type].add(node)
                if is_child(node_type, Matcher):
                    self.total += 1
                else:
                    self.others += 1
            else:
                self.duplicates += 1
        except:
            self.unhashable += 1
            
    def add_all(self, matcher):
        '''
        Add all nodes.
        '''
        for (_parent, child, type_) in dfs_edges(matcher, Matcher):
            self.add(type_, child)

    def __str__(self):
        counts = fmt('total:      {total:3d}\n'
                        'leaves:     {leaves:3d}\n'
                        'loops:      {loops:3d}\n'
                        'duplicates: {duplicates:3d}\n'
                        'others:     {others:3d}\n'
                        'unhashable: {unhashable:3d}\n', **self.__dict__)
        keys = list(self.types.keys())
        keys.sort(key=repr)
        types = '\n'.join([fmt('{0:40s}: {1:3d}', key, len(self.types[key]))
                           for key in keys])
        return counts + types
    
    def __eq__(self, other):
        '''
        Quick and dirty equality
        '''
        return str(self) == str(other)


class NodeStats2(object):
    '''
    Avoid using graph code (so we can check that...)
    '''
    
    def __init__(self, node):
        self.total = 0
        self.leaves = 0
        self.duplicates = 0
        self.types = {}

        known = set()
        stack = [node]
        while stack:
            node = stack.pop()
            if node in known:
                self.duplicates += 1
            else:
                known.add(node)
                self.total += 1
                type_ = type(node)
                if type_ not in self.types:
                    self.types[type_] = 0
                self.types[type_] += 1
                children = [child for child in node if isinstance(child, Matcher)]
                if not children:
                    self.leaves += 1
                else:
                    stack.extend(children)
        
    def __str__(self):
        counts = fmt('total:      {total:3d}\n'
                     'leaves:     {leaves:3d}\n'
                     'duplicates: {duplicates:3d}\n', **self.__dict__)
        keys = list(self.types.keys())
        keys.sort(key=repr)
        types = '\n'.join([fmt('{0:40s}: {1:3d}', key, self.types[key])
                           for key in keys])
        return counts + types
    
    def __eq__(self, other):
        '''
        Quick and dirty equality
        '''
        return str(self) == str(other)


#class DelayedClone(Visitor):    
#    '''
#    A version of `Clone()` that uses `Delayed()` rather
#    that `Proxy()` to handle circular references.  Also caches results to
#    avoid duplications.
#    '''
#    
#    def __init__(self, clone_=clone):
#        super(DelayedClone, self).__init__()
#        self._clone = clone_
#        self._visited = {}
#        self._loops = set()
#        self._node = None
#    
#    def loop(self, node):
#        '''
#        This is called for nodes that are involved in cycles when they are
#        needed as arguments but have not themselves been cloned.
#        '''
#        if node not in self._visited:
#            self._visited[node] = Delayed()
#            self._loops.add(node)
#        return self._visited[node]
#    
#    def node(self, node):
#        '''
#        Store the current node.
#        '''
#        self._node = node
#        
#    def constructor(self, *args, **kargs):
#        '''
#        Clone the node, taking care to handle loops.
#        '''
#        if self._node not in self._visited:
#            self._visited[self._node] = self.__clone_node(args, kargs)
#        # if this is one of the loops we replaced with a delayed instance,
#        # then we need to patch the delayed matcher
#        elif self._node in self._loops and \
#                not self._visited[self._node].matcher:
#            self._visited[self._node] += self.__clone_node(args, kargs)
#        return self._visited[self._node]
#    
#    def __clone_node(self, args, kargs):
#        '''
#        Before cloning, drop any Delayed from args and kargs.  Afterwards,
#        check if this is a Delaed instance and, if so, return the contents.
#        This helps keep the number of Delayed instances from exploding.
#        '''
##        args = lmap(self.__drop, args)
##        kargs = dict((key, self.__drop(kargs[key])) for key in kargs)
##        return self.__drop(self._clone(self._node, args, kargs))
#        return self._clone(self._node, args, kargs)
#    
#    # not needed now Delayed dynamically sets _match()
#    # also, will break new cloning
##    @staticmethod
##    def __drop(node):
##        '''
##        Filter `Delayed` instances where possible (if they have the matcher
##        defined and are nor transformed).
##        '''
##        # delayed import to avoid dependency loops
##        from lepl.matchers.transform import Transformable
##        if isinstance(node, Delayed) and node.matcher and \
##                not (isinstance(node, Transformable) and node.wrapper):
##            return node.matcher
##        else:
##            return node
#    
#    def leaf(self, value):
#        '''
#        Leaf values are unchanged.
#        '''
#        return value
    
    
