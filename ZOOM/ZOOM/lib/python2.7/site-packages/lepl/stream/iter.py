
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
A stream for iterable sources.  Each value in the iteration is considered as 
a line (which makes sense for files, for example, which iterate over lines).

The source is wrapped in a `Cons` object.  This has an attribute `head`
which contains the current line and a method `tail()` which returns another
`Cons` instance, or raise a `StopIteration`.

The stream has the form `(state, helper)`, where `helper` is an 
`IterableHelper` instance, as described below.

The `state` value in the stream described above has the form
`(cons, line_stream)` where `cons` is a `Cons` instance and line_stream
is a stream generated from `cons.head` (so has the structure (state', helper')
where state' and helper' depend on the type of the line and the stream factory
used).

Evaluation of stream methods then typically has the form:
- call to IterableHelper
- unpacking of state
- delegation to line_stream
- possible exception handling 

This has the  advantages of being generic in the type returned by the
iterator, of being customizable (by specifying a new factory), and re-using
existing code where possible (in the use of the sub-helper).  It should even
be possible to have iterables of iterables...
'''

from lepl.support.lib import add_defaults, fmt
from lepl.stream.simple import OFFSET, LINENO, BaseHelper
from lepl.stream.core import s_delta, s_kargs, s_fmt, s_debug, s_next, \
    s_line, s_join, s_empty, s_eq, HashKey


class Cons(object):
    '''
    A linked list cell that is a lazy wrapper around an iterable.  So "tail"
    returns the next iterable on demand.
    '''
    
    __slots__ = ['_iterable', '_head', '_tail', '_expanded']
    
    def __init__(self, iterable):
        self._iterable = iterable
        self._head = None
        self._tail = None
        self._expanded = False
        
    def _expand(self):
        if not self._expanded:
            self._head = next(self._iterable)
            self._tail = Cons(self._iterable)
            self._expanded = True
    
    @property
    def head(self):
        self._expand()
        return self._head
    
    @property
    def tail(self):
        self._expand()
        return self._tail


def base_iterable_factory(state_to_line_stream, type_):
    '''
    `IterableHelper` and the token helper differ mainly in how they map from 
    `state` to `line_stream`.
    '''
    
    class BaseIterableHelper(BaseHelper):
    
        def __init__(self, id=None, factory=None, max=None, global_kargs=None, 
                     cache_level=None, delta=None):
            super(BaseIterableHelper, self).__init__(id=id, factory=factory, 
                    max=max, global_kargs=global_kargs, 
                    cache_level=cache_level, delta=delta)
            add_defaults(self.global_kargs, {
                'global_type': type_,
                'filename': type_})
            self._kargs = dict(self.global_kargs)
            add_defaults(self._kargs, {'type': type_})
            
        def key(self, state, other):
            try:
                line_stream = state_to_line_stream(state)
                offset = s_delta(line_stream)[OFFSET]
            except StopIteration:
                self._warn('Default hash')
                offset = -1
            key = HashKey(self.id ^ offset ^ hash(other), (self.id, other))
            #self._debug(fmt('Hash at {0!r} ({1}): {2}', state, offset, hash(key)))
            return key
        
        def kargs(self, state, prefix='', kargs=None):
            line_stream = state_to_line_stream(state)
            return s_kargs(line_stream, prefix=prefix, kargs=kargs)
    
        def fmt(self, state, template, prefix='', kargs=None):
            line_stream = state_to_line_stream(state)
            return s_fmt(line_stream, template, prefix=prefix, kargs=kargs)
        
        def debug(self, state):
            try:
                line_stream = state_to_line_stream(state)
                return s_debug(line_stream)
            except StopIteration:
                return '<EOS>'
        
        def join(self, state, *values):
            line_stream = state_to_line_stream(state)
            return s_join(line_stream, *values)
        
        def empty(self, state):
            try:
                self.next(state)
                return False
            except StopIteration:
                return True
        
        def delta(self, state):
            line_stream = state_to_line_stream(state)
            return s_delta(line_stream)
        
        def eq(self, state1, state2):
            line_stream1 = state_to_line_stream(state1)
            line_stream2 = state_to_line_stream(state2)
            return s_eq(line_stream1, line_stream2)
        
        def deepest(self):
            return self.max.get()
        
        def new_max(self, state):
            return (self.max, 
                    (state, type(self)(id=self.id, factory=self.factory,
                                       max=None, delta=self.delta,
                                       global_kargs=self.global_kargs,
                                       cache_level=self.cache_level)))
    
    return BaseIterableHelper


class IterableHelper(
        base_iterable_factory(lambda state: state[1], '<iterable>')):
    '''
    Implement a stream over iterable values.
    '''
    
    def _next_line(self, cons, empty_line_stream):
        delta = s_delta(empty_line_stream)
        delta = (delta[OFFSET], delta[LINENO]+1, 1)
        return self.factory(cons.head, id=self.id, factory=self.factory,
                            max=self.max, global_kargs=self.global_kargs, 
                            delta=delta)
    
    def next(self, state, count=1):
        (cons, line_stream) = state
        try:
            (value, next_line_stream) = s_next(line_stream, count=count)
            return (value, ((cons, next_line_stream), self))
        except StopIteration:
            # the general approach here is to take what we can from the
            # current line, create the next, and take the rest from that.
            # of course, that may also not have enough, in which case it
            # will recurse.
            cons = cons.tail
            if s_empty(line_stream):
                next_line_stream = self._next_line(cons, line_stream)
                next_stream = ((cons, next_line_stream), self)
                return s_next(next_stream, count=count)
            else:
                (line, end_line_stream) = s_line(line_stream, False)
                next_line_stream = self._next_line(cons, end_line_stream)
                next_stream = ((cons, next_line_stream), self)
                (extra, final_stream) = s_next(next_stream, count=count-len(line))
                value = s_join(line_stream, line, extra)
                return (value, final_stream)
    
    def line(self, state, empty_ok):
        try:
            (cons, line_stream) = state
            if s_empty(line_stream):
                cons = cons.tail
                line_stream = self._next_line(cons, line_stream)
            (value, empty_line_stream) = s_line(line_stream, empty_ok)
            return (value, ((cons, empty_line_stream), self))
        except StopIteration:
            if empty_ok:
                raise TypeError('Iterable stream cannot return an empty line')
            else:
                raise
    
    def len(self, state):
        self._error('len(iter)')
        raise TypeError
        
    def stream(self, state, value, id_=None, max=None):
        (cons, line_stream) = state
        id_ = self.id if id_ is None else id_
        max = max if max else self.max
        next_line_stream = \
            self.factory(value, id=id_, factory=self.factory, max=max, 
                         global_kargs=self.global_kargs, 
                         cache_level=self.cache_level+1,
                         delta=s_delta(line_stream))
        return ((cons, next_line_stream), self)
    
