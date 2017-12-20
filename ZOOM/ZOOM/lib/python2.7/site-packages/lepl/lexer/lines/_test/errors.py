
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
A test related to error handling, based on a bug report.
'''

from logging import basicConfig, DEBUG
from sys import exc_info
from unittest import TestCase

from lepl import *


class ErrorTest(TestCase):
    
    def make_parser(self):
        
        with TraceVariables(False):
            introduce = ~Token(':')
            hash = Token('#.*')
            
            InvalidName = Token('[0-9_][a-zA-Z0-9_]*')
            name = Or(Token('[a-zA-Z][a-zA-Z0-9_]*'),
                      InvalidName ** make_error( 'InvalidName' ))
            
            typename = Or(Token(Literal('int')),
                          Token(Literal('bool')))
            
            memberdef = Line(typename & name) > tuple
            
            block = Delayed()
            
            line = (Line(name) | block)
            
            BlockStart = Or(Line(name & introduce),
                            Line(name) ** make_error('BlockStart-OnlyName'),
                            Line(introduce) ** make_error('BlockStart-OnlyColon'))
            block += BlockStart & (Block(memberdef) > list)
            
            program = (line[:] & Eos()) >> sexpr_throw
            program.config.lines(block_policy=explicit)
            
            return program.get_parse_string()
    
    def test_valid(self):
        '''
        There was a bug here with sexpr_throw, which didn't iterate correctly 
        over generators.
        '''
        #basicConfig(level=DEBUG)
        p = self.make_parser()
        #print(p.matcher.tree())
        result = p('foo:\n  int i' )
        assert result == ['foo', [('int', 'i')]], result
        
    def test_error(self):
        p = self.make_parser()
        try:
            result = p('foo\n  int i')
            assert False, 'no error'
        except Error:
            error = exc_info()[1]
            assert str(error) == "BlockStart-OnlyName (<string>, line 1)", str(error)
            
