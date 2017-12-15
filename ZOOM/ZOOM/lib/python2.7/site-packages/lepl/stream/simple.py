
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
Default implementation of the helper classes for sequences (strings and lists).

The state is an integer offset.  Sequence and a possible delta for the 
offset are stored in the helper.
'''

from itertools import chain

from lepl.support.lib import fmt, add_defaults, str, LogMixin
from lepl.stream.core import StreamHelper, OFFSET, LINENO, CHAR, HashKey


class BaseHelper(LogMixin, StreamHelper):
    
    def __init__(self, id=None, factory=None, max=None, global_kargs=None, 
                 cache_level=None, delta=None):
        super(BaseHelper, self).__init__(id=id, factory=factory, max=max, 
                global_kargs=global_kargs, cache_level=cache_level)
        self._delta = delta if delta else (0,1,1)


class SequenceHelper(BaseHelper):
    
    def __init__(self, sequence, id=None, factory=None, max=None, 
                 global_kargs=None, cache_level=None, delta=None):
        super(SequenceHelper, self).__init__(id=id, factory=factory, max=max,
                global_kargs=global_kargs, cache_level=cache_level, delta=delta)
        self._sequence = sequence
        type_ = self._typename(sequence)
        add_defaults(self.global_kargs, {
            'global_type': type_,
            'filename': type_})
        self._kargs = dict(self.global_kargs)
        add_defaults(self._kargs, {'type': type_})

    def key(self, state, other):
        # avoid confusion with incremental ids 
        offset = (state + self._delta[OFFSET]) << 16
        key = HashKey(self.id ^ offset ^ hash(other), (self.id, hash(other)))
        #self._debug(fmt('Hash at offset {0}: {1}', offset, hash(key)))
        return key
    
    def _fmt(self, sequence, offset, maxlen=60, left='', right='', index=True):
        '''fmt a possibly long subsection of data.'''
        if not sequence:
            if index:
                return fmt('{0!r}[{1:d}]', sequence, offset)
            else:
                return fmt('{0!r}', sequence)
        if offset >= 0 and offset < len(sequence):
            centre = offset
        elif offset > 0:
            centre = len(sequence) - 1
        else:
            centre = 0
        begin, end = centre, centre+1
        longest = None
        while True:
            if begin > 0:
                if end < len(sequence):
                    template = '{0!s}...{1!s}...{2!s}'
                else:
                    template = '{0!s}...{1!s}{2!s}'
            else:
                if end < len(sequence):
                    template = '{0!s}{1!s}...{2!s}'
                else:
                    template = '{0!s}{1!s}{2!s}'
            body = repr(sequence[begin:end])[len(left):]
            if len(right):
                body = body[:-len(right)]
            text = fmt(template, left, body, right, offset)
            if index:
                text = fmt('{0!s}[{1:d}:]', text, offset)
            if longest is None or len(text) <= maxlen:
                longest = text
            if len(text) > maxlen:
                return longest
            begin -= 1
            end += 1
            if begin < 0 and end > len(sequence):
                return longest
            begin = max(begin, 0)
            end = min(end, len(sequence))
                
    def _location(self, kargs, prefix):
        '''Location (separate method so subclasses can replace).'''
        return fmt('offset {' + prefix + 'global_offset}, value {' + prefix + 'repr}',
                      **kargs)
    
    def _typename(self, instance):
        if isinstance(instance, list) and instance:
            return fmt('<list{0}>', self._typename(instance[0]))
        else:
            try:
                return fmt('<{0}>', instance.__class__.__name__)
            except:
                return '<unknown>'
    
    def kargs(self, state, prefix='', kargs=None):
        '''
        Generate a dictionary of values that describe the stream.  These
        may be extended by subclasses.  They are provided to 
        `syntax_error_kargs`, for example.
        
        Note: Calculating this can be expensive; use only for error messages,
        not debug messages (that may be discarded).
        
        Implementation note: Because some values are 
        '''
        offset = state + self._delta[OFFSET]
        if kargs is None: kargs = {}
        add_defaults(kargs, self._kargs, prefix=prefix)
        within = offset > -1 and offset < len(self._sequence)
        data = self._fmt(self._sequence, state)
        text = self._fmt(self._sequence, state, index=False)
        # some values below may be already present in self._global_kargs
        defaults = {'data': data,
                    'global_data': data,
                    'text': text,
                    'global_text': text,
                    'offset': state,
                    'global_offset': offset,
                    'rest': self._fmt(self._sequence[offset:], 0, index=False),
                    'repr': repr(self._sequence[offset]) if within else '<EOS>',
                    'str': str(self._sequence[offset]) if within else '',
                    'lineno': 1,
                    'char': offset+1}
        add_defaults(kargs, defaults, prefix=prefix)
        add_defaults(kargs, {prefix + 'location': self._location(kargs, prefix)})
        return kargs
    
    def next(self, state, count=1):
        new_state = state+count
        if new_state <= len(self._sequence):
            stream = (new_state, self)
            self.max.update(self._delta[OFFSET] + new_state - 1, stream)
            return (self._sequence[state:new_state], stream)
        else:
            raise StopIteration
    
    def join(self, state, *values):
        assert values, 'Cannot join zero general sequences'
        result = values[0]
        for value in values[1:]:
            result += value
        return result
    
    def empty(self, state):
        return state >= len(self._sequence)
    
    def line(self, state, empty_ok):
        '''Returns the rest of the data.'''
        new_state = len(self._sequence)
        if state < new_state or (empty_ok and state == new_state):
            stream = (new_state, self)
            self.max.update(self._delta[OFFSET] + new_state, stream)
            return (self._sequence[state:new_state], stream)
        else:
            raise StopIteration
        
    def len(self, state):
        return len(self._sequence) - state
    
    def stream(self, state, value, id_=None, max=None):
        id_ = self.id if id_ is None else id_
        max = max if max else self.max
        # increment the cache level to expose lower level streams
        return self.factory(value, id=id_, factory=self.factory, 
                            max=max, global_kargs=self.global_kargs,
                            cache_level=self.cache_level+1,
                            delta=self.delta(state))
        
    def deepest(self):
        return self.max.get()
    
    def debug(self, state):
        try:
            return fmt('{0:d}:{1!r}', state, self._sequence[state])
        except IndexError:
            return fmt('{0:d}:<EOS>', state)
        
    def delta(self, state):
        offset = state + self._delta[OFFSET]
        return (offset, 1, offset+1)
    
    def new_max(self, state):
        return (self.max,
                (state, type(self)(self._sequence, id=self.id, 
                                   factory=self.factory, max=None,
                                   global_kargs=self.global_kargs, 
                                   delta=self._delta)))

    
    
class StringHelper(SequenceHelper):
    '''
    String-specific fmtting and location.
    '''
    
    def __init__(self, sequence, id=None, factory=None, max=None, 
                 global_kargs=None, cache_level=None, delta=None):
        # avoid duplicating processing on known strings
        if id is None:
            id = hash(sequence)
        super(StringHelper, self).__init__(sequence, id=id, factory=factory, 
                max=max, global_kargs=global_kargs, cache_level=cache_level, 
                delta=delta)

    def _fmt(self, sequence, offset, maxlen=60, left="'", right="'", index=True):
        return super(StringHelper, self)._fmt(sequence, offset, maxlen=maxlen, 
                                        left=left, right=right, index=index)
        
    def _location(self, kargs, prefix):
        return fmt('line {' + prefix + 'lineno:d}, character {' + prefix + 'char:d}', **kargs)
    
    def delta(self, state):
        offset = self._delta[OFFSET] + state
        lineno = self._delta[LINENO] + self._sequence.count('\n', 0, state)
        start = self._sequence.rfind('\n', 0, state)
        if start > -1:
            char = state - start
        else:
            char = self._delta[CHAR] + state
        return (offset, lineno, char)
        
    def kargs(self, state, prefix='', kargs=None):
        if kargs is None: kargs = {}
        (_, lineno, char) = self.delta(state)
        start = self._sequence.rfind('\n', 0, state) + 1 # omit \n
        end = self._sequence.find('\n', state) # omit \n
        # all is str() because passed to SyntaxError constructor
        if end < 0:
            rest = repr(self._sequence[state:])
            all = str(self._sequence[start:])
        else:
            rest = repr(self._sequence[state:end])
            all = str(self._sequence[start:end])
        add_defaults(kargs, {
            'type': '<string>',
            'filename': '<string>',
            'rest': rest,
            'all': all,
            'lineno': lineno,
            'char': char}, prefix=prefix)
        return super(StringHelper, self).kargs(state, prefix=prefix, kargs=kargs)
    
    def join(self, state, *values):
        return str().join(values)
    
    def line(self, state, empty_ok):
        '''Returns up to, and including then next \n'''
        max_len = len(self._sequence)
        if state < max_len or (empty_ok and state == max_len):
            end = self._sequence.find('\n', state) + 1
            if not end: end = len(self._sequence)
            return (self._sequence[state:end], (end, self))
        else:
            raise StopIteration

    def stream(self, state, value, id_=None, max=None):
        id_ = self.id if id_ is None else id_
        max = max if max else self.max
        return self.factory(value,  id=id_, factory=self.factory, 
                            max=max, global_kargs=self.global_kargs, 
                            delta=self.delta(state))
        
    
class ListHelper(SequenceHelper):
    '''
    List-specific fprmatting
    '''
    
    def _fmt(self, sequence, offset, maxlen=60, left="[", right="]", index=True):
        return super(ListHelper, self)._fmt(sequence, offset, maxlen=maxlen, 
                                            left=left, right=right, index=index)

    def join(self, state, *values):
        return list(chain(*values))
    

