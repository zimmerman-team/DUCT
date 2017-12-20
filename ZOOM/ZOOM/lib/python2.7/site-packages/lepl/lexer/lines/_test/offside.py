
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
Tests for offside parsing.
'''

from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.lexer.matchers import Token
from lepl.matchers.combine import Or
from lepl.matchers.core import Delayed
from lepl.matchers.derived import Letter, Digit
from lepl.matchers.monitor import Trace
from lepl.lexer.lines.matchers import Block, Line, explicit, \
    ContinuedLineFactory


# pylint: disable-msg=R0201
# unittest convention
class OffsideTest(TestCase):
    '''
    Test lines and blocks.
    '''
    
    def simple_grammar(self):
        '''
        Test a simple example: letters introduce numbers in an indented block.
        '''
        #basicConfig(level=DEBUG)
        
        number = Token(Digit())
        letter = Token(Letter())
        
        # the simplest whitespace grammar i can think of - lines are either
        # numbers (which are single, simple statements) or letters (which
        # mark the start of a new, indented block).
        block = Delayed()
        line = Or(Line(number), 
                  Line(letter) & block) > list
        # and a block is simply a collection of lines, as above
        block += Block(line[1:])
        
        program = Trace(line[1:])
        program.config.lines(block_policy=1)
        return program
        
    def test_single_line(self):
        program = self.simple_grammar()
        text = '''1'''
        parser = program.get_parse_string()
        result = parser(text)
        assert result == [['1']], result

    def test_two_lines(self):
        program = self.simple_grammar()
        text = '''1
2
'''
        parser = program.get_parse_string()
        result = parser(text)
        assert result == [['1'], 
                          ['2']], result
                                
    def test_single_block(self):
        #basicConfig(level=DEBUG)
        program = self.simple_grammar()
        text = '''a
 3
'''
        parser = program.get_parse_string()
        result = parser(text)
        assert result == [['a', ['3']]], result

    def test_bline(self):
        program = self.simple_grammar()
        text = '''1
2
a
 3
 b
  4
  5
 6
'''
        parser = program.get_parse_string()
        result = parser(text)
        assert result == [['1'], 
                          ['2'], 
                          ['a', ['3'], 
                                ['b', ['4'], 
                                      ['5']], 
                                ['6']]], result
                                
    def test_explicit(self):
        #basicConfig(level=DEBUG)
        number = Token(Digit())
        letter = Token(Letter())
        
        block = Delayed()
        line = Or(Line(number), 
                  Line(letter) & block) > list
        block += Block(line[1:])
        
        program = Trace(line[1:])
        
        text = '''1
2
a
 3
 b
  4
  5
 6
'''
        program.config.lines(block_policy=explicit)
        parser = program.get_parse_string()
        result = parser(text)
        assert result == [['1'], 
                          ['2'], 
                          ['a', ['3'], 
                                ['b', ['4'], 
                                      ['5']], 
                                ['6']]], result
                                
    def test_continued_explicit(self):
        number = Token(Digit())
        letter = Token(Letter())
        
        block = Delayed()
        bline = ContinuedLineFactory(r'x')
        line = Or(bline(number), 
                  bline(letter) & block) > list
        block += Block(line[1:])
        
        program = Trace(line[1:])
        
        text = '''1
2
a
 3
 b
  4
  5
 6
'''
        program.config.lines(block_policy=explicit)
        parser = program.get_parse_string()
        result = parser(text)
        assert result == [['1'], 
                          ['2'], 
                          ['a', ['3'], 
                                ['b', ['4'], 
                                      ['5']], 
                                ['6']]], result
