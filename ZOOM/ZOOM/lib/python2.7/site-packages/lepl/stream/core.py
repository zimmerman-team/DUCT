
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
Default implementations of the stream classes. 

A stream is a tuple (state, helper), where `state` will vary from location to 
location, while `helper` is an "unchanging" instance of `StreamHelper`, 
defined below.

For simple streams state can be a simple integer and this approach avoids the
repeated creation of objects.  More complex streams may choose to not use
the state at all, simply creating a new helper at each point.
'''

from abc import ABCMeta

from lepl.support.lib import fmt


#class _SimpleStream(metaclass=ABCMeta):
# Python 2.6
# pylint: disable-msg=W0105, C0103
_StreamHelper = ABCMeta('_StreamHelper', (object, ), {})
'''ABC used to identify streams.'''

DUMMY_HELPER = object()
'''Allows tests to specify an arbitrary helper in results.'''
    
OFFSET, LINENO, CHAR = range(3)
'''Indices into delta.'''


class StreamHelper(_StreamHelper):
    '''
    The interface that all helpers should implement.
    '''
    
    def __init__(self, id=None, factory=None, max=None, global_kargs=None,
                 cache_level=None):
        from lepl.stream.factory import DEFAULT_STREAM_FACTORY
        self.id = id if id is not None else hash(self)
        self.factory = factory if factory else DEFAULT_STREAM_FACTORY
        self.max = max if max else MutableMaxDepth()
        self.global_kargs = global_kargs if global_kargs else {}
        self.cache_level = 1 if cache_level is None else cache_level
    
    def __repr__(self):
        '''Simplify for comparison in tests'''
        return '<helper>'
    
    def __eq__(self, other):
        return other is DUMMY_HELPER or super(StreamHelper, self).__eq__(other)
    
    def __hash__(self):
        return super(StreamHelper, self).__hash__()

    def key(self, state, other):
        '''
        Generate an object that can be hashed (implements __hash__ and __eq__).
        See `HashKey`.
        '''
        raise NotImplementedError
    
    def kargs(self, state, prefix='', kargs=None):
        '''
        Generate a dictionary of values that describe the stream.  These
        may be extended by subclasses.  They are provided to 
        `syntax_error_kargs`, for example.
        
        `prefix` modifies the property names
        
        `kargs` allows values to be provided.  These are *not* overwritten,
        so if there is a name clash the provided value remains.
        
        Note: Calculating this can be expensive; use only for error messages,
        not debug messages (that may be discarded).
        
        The following names will be defined (at a minimum).
        
        For these value the "global" prefix indicates the underlying stream 
        when, for example, tokens are used (other values will be relative to 
        the token).  If tokens etc are not in use then global and non-global 
        values will agree.
        - data: a line representing the data, highlighting the current offset
        - global_data: as data, but for the entire sequence
        - text: as data, but without a "[...]" at the end
        - global_text: as text, but for the entire sequence
        - type: the type of the sequence
        - global_type: the type of the entire sequence
        - global_offset: a 0-based index into the underlying sequence

        These values are always local:
        - offset: a 0-based index into the sequence
        - rest: the data following the current point
        - repr: the current value, or <EOS>
        - str: the current value, or an empty string
        
        These values are always global:
        - filename: a filename, if available, or the type
        - lineno: a 1-based line number for the current offset
        - char: a 1-based character count within the line for the current offset
        - location: a summary of the current location
        '''
        raise NotImplementedError

    def fmt(self, state, template, prefix='', kargs=None):
        '''fmt a message using the expensive kargs function.'''
        return fmt(template, **self.kargs(state, prefix=prefix, kargs=kargs))
    
    def debug(self, state):
        '''Generate an inexpensive debug message.'''
        raise NotImplementedError
    
    def next(self, state, count=1):
        '''
        Return (value, stream) where `value` is the next value (or 
        values if count > 1) from the stream and `stream` is advanced to the
        next character.  Note that `value` is always a sequence (so if the 
        stream is a list of integers, and `count`=1, then it will be a 
        unitary list, for example).
        
        Should raise StopIteration when no more data are available.
        '''
        raise StopIteration
    
    def join(self, state, *values):
        '''
        Join sequences of values into a single sequence.
        '''
        raise NotImplementedError
    
    def empty(self, state):
        '''
        Return true if no more data available.
        '''
        raise NotImplementedError
    
    def line(self, state, empty_ok):
        '''
        Return (values, stream) where `values` correspond to something
        like "the rest of the line" from the current point and `stream`
        is advanced to the point after the line ends.
        
        If `empty_ok` is true and we are at the end of a line, return an
        empty line, otherwise advance (and maybe raise a StopIteration).
        '''
        raise NotImplementedError
    
    def len(self, state):
        '''
        Return the remaining length of the stream.  Streams of unknown
        length (iterables) should raise a TypeError.
        '''
        raise NotImplementedError
    
    def stream(self, state, value, id_=None, max=None):
        '''
        Return a new stream that encapsulates the value given, starting at
        `state`.  IMPORTANT: the stream used is the one that corresponds to
        the start of the value.
          
        For example:
            (line, next_stream) = s_line(stream, False)
            token_stream = s_stream(stream, line) # uses stream, not next_stream
         
        This is used when processing Tokens, for example, or columns (where
        fragments in the correct column area are parsed separately).
        '''
        raise NotImplementedError
    
    def deepest(self):
        '''
        Return a stream that represents the deepest match.  The stream may be
        incomplete in some sense (it may not be possible to use it for
        parsing more data), but it will have usable fmt and kargs methods.
        '''
        raise NotImplementedError
    
    def delta(self, state):
        '''
        Return the offset, lineno and char of the current point, relative to 
        the entire stream, as a tuple. 
        '''
        raise NotImplementedError
    
    def eq(self, state1, state2):
        '''
        Are the two states equal?
        '''
        return state1 == state2
    
    def new_max(self, state):
        '''
        Return (old max, new stream), where new stream uses a new max.
        This is used when we want to read from the stream without 
        affecting the max (eg when looking ahead to generate tokens).
        '''
        raise NotImplementedError
    
    def cacheable(self):
        '''
        Is this stream cacheable?
        '''
        return self.cache_level > 0
    

# The following are helper functions that allow the methods above to be
# called on (state, helper) tuples

s_key = lambda stream, other=None: stream[1].key(stream[0], other)
'''Invoke helper.key(state, other)'''

s_kargs = lambda stream, prefix='', kargs=None: stream[1].kargs(stream[0], prefix=prefix, kargs=kargs)
'''Invoke helper.kargs(state, prefix, kargs)'''

s_fmt = lambda stream, template, prefix='', kargs=None: stream[1].fmt(stream[0], template, prefix=prefix, kargs=kargs)
'''Invoke helper.fmt(state, template, prefix, kargs)'''

s_debug = lambda stream: stream[1].debug(stream[0])
'''Invoke helper.debug()'''

s_next = lambda stream, count=1: stream[1].next(stream[0], count=count)
'''Invoke helper.next(state, count)'''

s_join = lambda stream, *values: stream[1].join(stream[0], *values)
'''Invoke helper.join(*values)'''

s_empty = lambda stream: stream[1].empty(stream[0])
'''Invoke helper.empty(state)'''

s_line = lambda stream, empty_ok: stream[1].line(stream[0], empty_ok)
'''Invoke helper.line(state, empty_ok)'''

s_len = lambda stream: stream[1].len(stream[0])
'''Invoke helper.len(state)'''

s_stream = lambda stream, value, id_=None, max=None: stream[1].stream(stream[0], value, id_=id_, max=max)
'''Invoke helper.stream(state, value)'''

s_deepest = lambda stream: stream[1].deepest()
'''Invoke helper.deepest()'''

s_delta = lambda stream: stream[1].delta(stream[0])
'''Invoke helper.delta(state)'''

s_eq = lambda stream1, stream2: stream1[1].eq(stream1[0], stream2[0])
'''Compare two streams (which should have identical helpers)'''

s_id = lambda stream: stream[1].id
'''Access the ID attribute.'''

s_factory = lambda stream: stream[1].factory
'''Access the factory attribute.'''

s_max = lambda stream: stream[1].max
'''Access the max attribute.'''

s_new_max = lambda stream: stream[1].new_max(stream[0])
'''Invoke helper.new_max(state).'''

s_global_kargs = lambda stream: stream[1].global_kargs
'''Access the global_kargs attribute.'''

s_cache_level = lambda stream: stream[1].cache_level
'''Access the cache_level attribute.'''

s_cacheable = lambda stream: stream[1].cacheable()
'''Is the stream cacheable?'''


class MutableMaxDepth(object):
    '''
    Track maximum depth (offset) reached and the associated stream.  Used to
    generate error message for incomplete matches.
    '''
    
    def __init__(self):
        self.depth = 0
        self.stream = None
        
    def update(self, depth, stream):
        # the '=' here allows a token to nudge on to the next stream without
        # changing the offset (when count=0 in s_next)
        if depth >= self.depth or not self.stream:
            self.depth = depth
            self.stream = stream
        
    def get(self):
        return self.stream
    

class HashKey(object):
    '''
    Used to store a value with a given hash.
    '''
    
    __slots__ = ['hash', 'eq']
    
    def __init__(self, hash, eq=None):
        self.hash = hash
        self.eq = eq
        
    def __hash__(self):
        return self.hash
    
    def __eq__(self, other):
        try:
            return other.hash == self.hash and other.eq == self.eq
        except AttributeError:
            return False
        
        
