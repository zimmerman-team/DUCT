
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,W0621,R0903
# (the code style is for documentation, not "real")
#@PydevCodeAnalysisIgnore

'''
Examples from the documentation.
'''

from logging import basicConfig, DEBUG, ERROR

from gc import collect
from random import random
from timeit import timeit

from lepl import *
from lepl._example.support import Example
from lepl.support.lib import fmt


NUMBER = 10
REPEAT = 3

def matcher():
    '''A simple parser we'll use as an example.'''
    
    class Term(List): pass
    class Factor(List): pass
    class Expression(List): pass
        
    expr   = Delayed()
    number = Float()                                >> float
    
    with DroppedSpace():
        term    = number | '(' & expr & ')'         > Term
        muldiv  = Any('*/')
        factor  = term & (muldiv & term)[:]         > Factor
        addsub  = Any('+-')
        expr   += factor & (addsub & factor)[:]     > Expression
        line    = expr & Eos()
    
    return line

if __name__ == '__main__':
    basicConfig(level=ERROR)
    m = matcher()
    print_timing(lambda: fmt('{0:4.2f} + {1:4.2f} * ({2:4.2f} + {3:4.2f} - {4:4.2f})',
                             random(), random(), random(), random(), random()),
                 {'default': m.clone(),
                  'clear': m.clone().config.clear().matcher,
                  'no memo': m.clone().config.no_memoize().matcher,
                  'low memory': m.clone().config.low_memory().matcher,
                  'nfa': m.clone().config.clear().compile_to_nfa().matcher,
                  'dfa': m.clone().config.clear().compile_to_dfa().matcher,
                  're': m.clone().config.clear().compile_to_re().matcher})


# pylint: disable-msg=E0601
# (pylint parsing bug?)        
class PerformanceExample(Example):
    
    def test_parse(self):
    
        # run this to make sure nothing changes
        m = matcher()
        parsers = [m.clone(), 
                   m.clone().config.clear().matcher, 
                   m.clone().config.no_memoize().matcher, 
                   m.clone().config.auto_memoize().matcher,
                   m.clone().config.low_memory().matcher]
        examples = [(lambda: parser.parse('1.23e4 + 2.34e5 * (3.45e6 + 4.56e7 - 5.67e8)')[0],
"""Expression
 +- Factor
 |   `- Term
 |       `- 12300.0
 +- '+'
 `- Factor
     +- Term
     |   `- 234000.0
     +- '*'
     `- Term
         +- '('
         +- Expression
         |   +- Factor
         |   |   `- Term
         |   |       `- 3450000.0
         |   +- '+'
         |   +- Factor
         |   |   `- Term
         |   |       `- 45600000.0
         |   +- '-'
         |   `- Factor
         |       `- Term
         |           `- 567000000.0
         `- ')'""") for parser in parsers]
        self.examples(examples)
            