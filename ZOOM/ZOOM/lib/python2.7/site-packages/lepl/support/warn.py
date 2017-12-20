
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
A mechanism to associate warnings with certain classes (eg for deprecation)
and to disable those warnings.
'''

from logging import getLogger

from lepl.support.lib import fmt


_WARNINGS = {}
LOG = getLogger(__name__)


class Warning(object):
    
    def __init__(self, name, message):
        super(Warning, self).__init__()
        self.silent = False
        self.displayed = False
        self.name = name
        self.message = message
        assert self.name not in _WARNINGS, (self.name, _WARNINGS)
        _WARNINGS[self.name] = self
        
    def warn(self):
        if not self.silent and not self.displayed:
            print(self.message)
            print(fmt('To disable this message call '
                         'lepl.support.warn.silence({0!r})', self.name)) 
            self.displayed = True
            
            
def silence(name):
    '''
    Silence the warning.  Obviously, don't do this until you have addressed the
    underlying issue...
    '''
    if name in _WARNINGS:
        _WARNINGS[name].silent = True
    else:
        LOG.warn(fmt('No warning registered for {0}', name))


def warn_on_use(message, name=None):
    '''
    A decorator that warns when the function is used.
    '''
    def decorator(func, name=name):
        if name is None:
            name = func.__name__
        warning = Warning(name, message)
        def wrapper(*args, **kargs):
            warning.warn()
            return func(*args, **kargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


