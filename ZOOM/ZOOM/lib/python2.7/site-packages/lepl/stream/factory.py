
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


from collections import Iterable

from lepl.stream.simple import SequenceHelper, StringHelper, ListHelper
from lepl.stream.iter import IterableHelper, Cons
from lepl.support.lib import basestring, fmt, add_defaults, file
from lepl.lexer.stream import TokenHelper


class StreamFactory(object):
    '''
    Given a value (typically a sequence), generate a stream.
    '''
    
    def from_string(self, text, **kargs):
        '''
        Provide a stream for the contents of the string.
        '''
        add_defaults(kargs, {'factory': self})
        return (0, StringHelper(text, **kargs))

    def from_list(self, list_, **kargs):
        '''
        Provide a stream for the contents of the list.
        '''
        add_defaults(kargs, {'factory': self})
        return (0, ListHelper(list_, **kargs))

    def from_sequence(self, sequence, **kargs):
        '''
        Return a generic stream for any indexable sequence.
        '''
        add_defaults(kargs, {'factory': self})
        return (0, SequenceHelper(sequence, **kargs))

    def from_iterable(self, iterable, **kargs):
        '''
        Provide a stream for the contents of the iterable.  This assumes that
        each value from the iterable is a "line" which will, in turn, be
        passed to the stream factory.
        '''
        add_defaults(kargs, {'factory': self})
        cons = Cons(iterable)
        return ((cons, self(cons.head, **kargs)), IterableHelper(**kargs))
    
    def from_file(self, file_, **kargs):
        '''
        Provide a stream for the contents of the file.  There is no 
        corresponding `from_path` because the opening and closing of the
        path must be done outside the parsing (or the contents will become
        unavailable), so use instead:
          with open(path) as f:
              parser.parse_file(f)
        which will close the file after parsing.
        '''
        try:
            gkargs = kargs.get('global_kargs', {})
            add_defaults(gkargs, {'filename': file_.name})
            add_defaults(kargs, {'global_kargs': gkargs})
        except AttributeError:
            pass
        return self.from_iterable(file_, **kargs)
    
    def to_token(self, iterable, **kargs):
        '''
        Create a stream for tokens.  The `iterable` is a source of
        (token_ids, sub_stream) tuples, where `sub_stream` will be
        matched within the token.
        '''
        return (Cons(iterable), TokenHelper(**kargs))
            
    def __call__(self, sequence, **kargs):
        '''
        Auto-detect type and wrap appropriately.
        '''
        if isinstance(sequence, basestring):
            return self.from_string(sequence, **kargs)
        elif isinstance(sequence, list):
            return self.from_list(sequence, **kargs)
        elif isinstance(sequence, file):
            return self.from_file(sequence, **kargs)
        elif hasattr(sequence, '__getitem__') and hasattr(sequence, '__len__'):
            return self.from_sequence(sequence, **kargs)
        elif isinstance(sequence, Iterable):
            return self.from_iterable(sequence, **kargs)
        else:
            raise TypeError(fmt('Cannot generate a stream for type {0}',
                                   type(sequence)))

DEFAULT_STREAM_FACTORY = StreamFactory()
