
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
A facade that delegates all methods to an embedded instance.
'''

from lepl.stream.core import StreamHelper


class HelperFacade(StreamHelper):
    '''
    A facade that delegates all calls to the underlying delegate stream.
    '''
    
    def __init__(self, delegate):
        self._delegate = delegate
    
    def __repr__(self):
        return repr(self._delegate)
    
    def __eq__(self, other):
        return self._delegate == other
    
    def __hash__(self):
        return hash(self._delegate)

    def key(self, state, other):
        return self._delegate.key(state, other)
    
    def kargs(self, state, prefix='', kargs=None):
        return self._delegate.kargs(state, prefix=prefix, kargs=kargs)

    def fmt(self, state, template, prefix='', kargs=None):
        return self._delegate.fmt(state, template, prefix=prefix, kargs=kargs)
    
    def debug(self, state):
        return self._delegate.debug(state)
    
    def next(self, state, count=1):
        return self._delegate.next(state, count=count)
    
    def join(self, state, *values):
        return self._delegate.join(state, *values)
    
    def empty(self, state):
        return self._delegate.empty(state)
    
    def line(self, state, empty_ok):
        return self._delegate.line(state, empty_ok)
    
    def len(self, state):
        return self._delegate.len(state)
    
    def stream(self, state, value, id_=None):
        return self._delegate.stream(state, value, id_)

    def deepest(self):
        return self._delegate.deepest()
    
    def delta(self, state):
        return self._delegate.delta(state)
    
    def eq(self, state1, state2):
        return self._delegate.eq(state1, state2)
    
    def new_max(self, state):
        return self._delegate.new_max(state)
    
    def cacheable(self):
        return self._delegate.cacheable()
